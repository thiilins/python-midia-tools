"""
Compressor de vídeos para streaming web — H.264 + faststart.
Produz MP4 compatível com players web, permitindo seek antes do download completo.
"""

import json
import os
import re
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg
from ..common.resource_control import (
    usar_aceleracao_hardware,
    obter_cores_fisicos,
    obter_cores_encoder,
    definir_prioridade_processo,
)


class CompressorWebVideo:
    """
    Converte vídeos para H.264 + faststart, otimizado para streaming web.
    Suporta seek antes do download completo (moov atom no início do arquivo).
    """

    EXTENSOES_VALIDAS = {
        ".mp4", ".m4v", ".mov", ".mkv", ".avi", ".wmv",
        ".flv", ".webm", ".ts", ".mts", ".m2ts", ".3gp",
        ".vob", ".asf", ".ogv", ".rm", ".rmvb",
    }

    # Encoders H.264 GPU (em ordem de preferência AMD → NVIDIA → Intel)
    GPU_ENCODERS = ["h264_amf", "h264_nvenc", "h264_qsv", "h264_videotoolbox"]

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        crf: str = "22",
        preset: str = "medium",
        audio_bitrate: str = "192k",
    ):
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.crf = crf
        self.preset = preset
        self.audio_bitrate = audio_bitrate

        env_device = os.getenv("GPU_DEVICE", "").strip()
        self.gpu_device_idx = int(env_device) if env_device.isdigit() else 0

        self.encoder_gpu = None
        if usar_aceleracao_hardware():
            self.encoder_gpu = self._detectar_encoder_gpu()

        self.cores_fisicos = obter_cores_fisicos()
        self.cores_encoder = obter_cores_encoder()

        definir_prioridade_processo(nice=0)

    def _detectar_encoder_gpu(self) -> Optional[str]:
        encoder_forcado = os.getenv("GPU_ENCODER", "").strip().lower()
        if encoder_forcado:
            aliases = {
                "amd": "h264_amf", "amf": "h264_amf",
                "nvidia": "h264_nvenc", "nvenc": "h264_nvenc",
                "intel": "h264_qsv", "qsv": "h264_qsv",
            }
            if encoder_forcado in self.GPU_ENCODERS:
                return encoder_forcado
            if encoder_forcado in aliases:
                return aliases[encoder_forcado]

        try:
            resultado = subprocess.run(
                ["ffmpeg", "-encoders"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
            output = resultado.stdout + resultado.stderr
            for encoder in self.GPU_ENCODERS:
                if encoder in output:
                    return encoder
        except Exception:
            pass
        return None

    def _obter_info_video(self, arquivo: Path) -> Dict:
        comando = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_name,codec_type,width,height,bit_rate,r_frame_rate",
            "-show_entries", "format=duration,bit_rate,size",
            "-of", "json",
            str(arquivo),
        ]
        try:
            resultado = subprocess.run(
                comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, check=True, timeout=10,
            )
            data = json.loads(resultado.stdout)

            info: Dict = {
                "codec": None, "audio_codec": None,
                "width": None, "height": None,
                "duracao": None, "tamanho": None,
            }

            streams = data.get("streams", [])
            video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

            if video_stream:
                info["codec"] = video_stream.get("codec_name", "unknown")
                info["width"] = video_stream.get("width", 0)
                info["height"] = video_stream.get("height", 0)

            if audio_stream:
                info["audio_codec"] = audio_stream.get("codec_name")

            if "format" in data:
                fmt = data["format"]
                info["duracao"] = float(fmt.get("duration", 0))
                info["tamanho"] = int(fmt.get("size", 0))

            return info
        except Exception:
            return {"codec": "unknown", "audio_codec": None, "width": 0,
                    "height": 0, "duracao": 0, "tamanho": 0}

    def _converter_tempo_para_segundos(self, tempo_str: str) -> float:
        try:
            h, m, s = tempo_str.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        except ValueError:
            return 0.0

    def _construir_args_gpu(self, encoder: str) -> list:
        args = ["-c:v", encoder]
        if encoder == "h264_amf":
            qp = int(self.crf)
            args += [
                "-rc", "cqp",
                "-qp_i", str(qp),
                "-qp_p", str(qp + 2),
                "-qp_b", str(qp + 4),
                "-quality", "balanced",
                "-bf", "2",
            ]
        elif encoder == "h264_nvenc":
            args += ["-preset", "p4", "-rc:v", "vbr", "-cq", self.crf, "-b:v", "0"]
        elif encoder == "h264_qsv":
            args += ["-preset", "medium", "-global_quality", self.crf]
        elif encoder == "h264_videotoolbox":
            qualidade = max(40, min(85, int(100 - (int(self.crf) - 18) * 2.5)))
            args += ["-q:v", str(qualidade), "-allow_sw", "1"]
        return args

    def _converter_video(
        self, arquivo_entrada: Path, arquivo_saida: Path, duracao_total: float
    ) -> tuple:
        """
        Converte o vídeo para H.264 com faststart.

        Returns:
            (bool, Optional[str]): (sucesso, mensagem_erro)
        """
        comando = [
            "ffmpeg", "-y",
            "-analyzeduration", "150M",
            "-probesize", "150M",
        ]

        if self.encoder_gpu and "amf" in self.encoder_gpu:
            comando.extend([
                "-init_hw_device", f"d3d11va=dx:{self.gpu_device_idx}",
                "-init_hw_device", "amf=amf@dx",
            ])

        comando.extend(["-i", str(arquivo_entrada)])

        # Stream mapping: vídeo principal + todos os áudios + legendas (opcionais)
        comando.extend(["-map", "0:v:0", "-map", "0:a?", "-map", "0:s?"])

        # Codec de vídeo
        if self.encoder_gpu:
            comando.extend(self._construir_args_gpu(self.encoder_gpu))
        else:
            # libx264 com paralelismo via -threads (diferente do libx265 que usa pools)
            comando.extend([
                "-c:v", "libx264",
                "-preset", self.preset,
                "-crf", self.crf,
                "-threads", str(self.cores_encoder),
            ])

        # Formato de pixel — máxima compatibilidade com browsers e TVs
        comando.extend(["-pix_fmt", "yuv420p"])

        # Áudio AAC
        comando.extend(["-c:a", "aac", "-b:a", self.audio_bitrate])

        # Legendas
        comando.extend(["-c:s", "mov_text", "-ignore_unknown"])

        # Crítico para streaming: move moov atom para o início do arquivo
        comando.extend(["-movflags", "+faststart"])

        comando.extend(["-progress", "pipe:1", str(arquivo_saida)])

        regex_tempo = re.compile(r"out_time=(\d{2}:\d{2}:\d{2}\.\d+)")
        stderr_output: list = []
        stderr_lock = threading.Lock()

        def ler_stderr():
            try:
                for linha in processo.stderr:
                    with stderr_lock:
                        stderr_output.append(linha)
            except Exception:
                pass

        try:
            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            stderr_thread = threading.Thread(target=ler_stderr, daemon=True)
            stderr_thread.start()

            total = max(int(duracao_total), 1)
            with ProgressBar(
                total=total, unit="s",
                desc=f"🌐 {arquivo_entrada.name[:20]}...",
            ).context() as pbar:
                tempo_anterior = 0.0
                while True:
                    linha = processo.stdout.readline()
                    if not linha:
                        if processo.poll() is not None:
                            break
                        continue
                    match = regex_tempo.search(linha)
                    if match:
                        tempo_atual = self._converter_tempo_para_segundos(match.group(1))
                        tempo_atual = min(tempo_atual, duracao_total)
                        incremento = tempo_atual - tempo_anterior
                        if incremento > 0:
                            if pbar.n + incremento > total:
                                incremento = total - pbar.n
                            if incremento > 0:
                                pbar.update(incremento)
                            tempo_anterior = tempo_atual

                if pbar.n < total:
                    pbar.update(total - pbar.n)

            try:
                processo.wait(timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    processo.kill()
                    processo.wait(timeout=2)
                except Exception:
                    pass
                return False, "FFmpeg excedeu o tempo limite de espera"

            stderr_thread.join(timeout=2)

            with stderr_lock:
                stderr_text = "".join(stderr_output)

            if processo.returncode == 0:
                return True, None

            erro_msg = f"FFmpeg retornou código {processo.returncode}"
            if stderr_text:
                linhas_erro = [
                    l.strip() for l in stderr_text.split("\n")
                    if l.strip() and ("error" in l.lower() or "failed" in l.lower())
                ]
                if linhas_erro:
                    erro_msg += f": {linhas_erro[-1][:200]}"
            return False, erro_msg

        except Exception as e:
            with stderr_lock:
                if stderr_output:
                    stderr_text = "".join(stderr_output)
                    linhas_erro = [
                        l.strip() for l in stderr_text.split("\n")
                        if l.strip() and ("error" in l.lower() or "failed" in l.lower())
                    ]
                    if linhas_erro:
                        return False, f"Erro FFmpeg: {linhas_erro[-1][:200]}"
            return False, f"Erro ao executar FFmpeg: {str(e)}"

    def processar(self, deletar_originais: bool = True) -> dict:
        """
        Converte todos os vídeos da pasta de entrada para H.264 web-otimizado.

        Args:
            deletar_originais: Se True, apaga o original após conversão bem-sucedida.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not verificar_ffmpeg():
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            print(f"ℹ️  Pasta '{self.pasta_entrada}' criada. Adicione vídeos nela.")
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = sorted(
            (
                f for f in pasta_entrada.iterdir()
                if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
            ),
            key=lambda f: f.stat().st_size,
        )

        if not arquivos:
            print("ℹ️  Nenhum vídeo encontrado.")
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        encoder_info = (
            f"{self.encoder_gpu} (adapter {self.gpu_device_idx})"
            if self.encoder_gpu
            else f"libx264 (threads={self.cores_encoder}/{self.cores_fisicos} cores)"
        )

        print(f"\n🌐 Compressão web para {len(arquivos)} vídeo(s) — H.264 + faststart")
        print(f"⚙️  CRF {self.crf} | Preset {self.preset} | Áudio {self.audio_bitrate}")
        print(f"🔧 Encoder: {encoder_info}")
        print("-" * 60)

        sucessos = 0
        falhas = 0
        pulados = 0
        total_original_mb = 0.0
        total_novo_mb = 0.0

        for i, arquivo_origem in enumerate(arquivos, 1):
            arquivo_destino = pasta_saida / (arquivo_origem.stem + ".mp4")

            # Resume: pula arquivos já convertidos
            if arquivo_destino.exists() and arquivo_destino.stat().st_size > 0:
                print(f"\n[{i}/{len(arquivos)}] ⏭️  {arquivo_origem.name} — já convertido, pulando")
                pulados += 1
                continue

            info = self._obter_info_video(arquivo_origem)
            duracao = info.get("duracao") or 0
            tamanho_original = arquivo_origem.stat().st_size / (1024 * 1024)
            total_original_mb += tamanho_original

            resolucao = f"{info['width']}x{info['height']}" if info.get("width") else "?"
            print(f"\n[{i}/{len(arquivos)}] 📹 {arquivo_origem.name}")
            print(f"   Antes: {resolucao} | {info['codec']} | {tamanho_original:.2f}MB")

            sucesso, erro = self._converter_video(arquivo_origem, arquivo_destino, duracao)

            # Fallback CPU quando GPU falha
            if not sucesso and self.encoder_gpu:
                if arquivo_destino.exists():
                    try:
                        arquivo_destino.unlink()
                    except OSError:
                        pass
                print(f"   🔄 GPU falhou, tentando CPU (libx264)...")
                encoder_backup = self.encoder_gpu
                self.encoder_gpu = None
                sucesso, erro = self._converter_video(arquivo_origem, arquivo_destino, duracao)
                self.encoder_gpu = encoder_backup

            if sucesso and arquivo_destino.exists():
                tamanho_novo = arquivo_destino.stat().st_size / (1024 * 1024)
                reducao = 100 - (tamanho_novo / tamanho_original * 100)
                total_novo_mb += tamanho_novo

                print(f"   ✅ Finalizado. Redução: {reducao:.1f}% ({tamanho_original:.2f}MB → {tamanho_novo:.2f}MB)")

                if deletar_originais:
                    try:
                        arquivo_origem.unlink()
                        print("   🗑️  Original removido.")
                    except OSError:
                        pass
                sucessos += 1
            else:
                if arquivo_destino.exists():
                    try:
                        arquivo_destino.unlink()
                    except OSError:
                        pass
                print(f"   ❌ Erro: {erro}")
                falhas += 1

        print("\n" + "=" * 60)
        print(f"✅ Conversão web concluída!")
        print(f"   Sucessos: {sucessos} | Falhas: {falhas} | Pulados: {pulados}")
        if total_original_mb > 0 and sucessos > 0:
            economizado_mb = total_original_mb - total_novo_mb
            reducao_total = 100 - (total_novo_mb / total_original_mb * 100)
            def fmt(mb):
                return f"{mb / 1024:.2f}GB" if mb >= 1024 else f"{mb:.0f}MB"
            print(f"   💾 Total original:   {fmt(total_original_mb)}")
            print(f"   💾 Total convertido: {fmt(total_novo_mb)}")
            print(f"   🎉 Economizado:      {fmt(economizado_mb)} ({reducao_total:.1f}% menor)")

        return {"sucessos": sucessos, "falhas": falhas, "pulados": pulados,
                "economizado_mb": round(total_original_mb - total_novo_mb, 2)}
