"""
Corretor de vídeos - Correção de framerate e problemas gerais.
"""

import json
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg
from ..common.resource_control import (
    obter_configuracao_threads,
    obter_configuracao_limite_cpu,
    obter_configuracao_limite_memoria,
    obter_pausa_entre_videos,
    verificar_recursos_disponiveis,
    aguardar_recursos_disponiveis,
    definir_prioridade_processo,
    pausar_entre_processamentos,
)


class CorretorVideo:
    """
    Classe para corrigir problemas em vídeos (VFR, timestamps, áudio).
    """

    # Extensões suportadas
    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        corrigir_vfr: bool = True,
        corrigir_timestamps: bool = True,
        corrigir_audio: bool = True,
    ):
        """
        Inicializa o corretor.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            corrigir_vfr: Se True, corrige Variable Frame Rate.
            corrigir_timestamps: Se True, corrige problemas com timestamps.
            corrigir_audio: Se True, corrige dessincronia de áudio.
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.corrigir_vfr = corrigir_vfr
        self.corrigir_timestamps = corrigir_timestamps
        self.corrigir_audio = corrigir_audio

        # Configurações de controle de recursos
        self.threads = obter_configuracao_threads()
        self.limite_cpu = obter_configuracao_limite_cpu()
        self.limite_memoria = obter_configuracao_limite_memoria()
        self.pausa_entre_videos = obter_pausa_entre_videos()

        # Define prioridade do processo (menor prioridade = menos impacto no sistema)
        definir_prioridade_processo(nice=5)

    def _obter_info_video(self, arquivo: Path) -> Dict:
        """
        Obtém informações completas do vídeo em 1 chamada ffprobe.
        Inclui codec de áudio e fps raw para derivar detecção de problemas sem chamadas extras.
        """
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

            info = {
                "codec": None, "audio_codec": None,
                "width": None, "height": None,
                "bitrate_video": None, "bitrate_total": None,
                "fps": None, "fps_raw": None,
                "duracao": None, "tamanho": None,
            }

            streams = data.get("streams", [])
            video = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

            if video:
                info["codec"] = video.get("codec_name", "unknown")
                info["width"] = video.get("width", 0)
                info["height"] = video.get("height", 0)
                info["bitrate_video"] = video.get("bit_rate")
                if info["bitrate_video"]:
                    info["bitrate_video"] = int(info["bitrate_video"]) / 1000
                r = video.get("r_frame_rate", "")
                info["fps_raw"] = r
                if r and "/" in r:
                    num, den = map(int, r.split("/"))
                    if den > 0:
                        info["fps"] = round(num / den, 2)

            info["audio_codec"] = audio.get("codec_name") if audio else None

            if "format" in data:
                fmt = data["format"]
                info["duracao"] = float(fmt.get("duration", 0))
                info["bitrate_total"] = fmt.get("bit_rate")
                if info["bitrate_total"]:
                    info["bitrate_total"] = int(info["bitrate_total"]) / 1000
                info["tamanho"] = int(fmt.get("size", 0))

            return info
        except Exception:
            return {
                "codec": "unknown", "audio_codec": None,
                "width": 0, "height": 0,
                "bitrate_video": None, "bitrate_total": None,
                "fps": None, "fps_raw": None,
                "duracao": 0, "tamanho": 0,
            }

    def _converter_tempo_para_segundos(self, tempo_str: str) -> float:
        """
        Converte o formato HH:MM:SS.mm do FFmpeg para segundos totais.

        Args:
            tempo_str: String no formato HH:MM:SS.mm.

        Returns:
            float: Tempo em segundos.
        """
        try:
            h, m, s = tempo_str.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        except ValueError:
            return 0.0

    def detectar_problemas(self, arquivo: Path, info: Dict = None) -> Dict:
        """
        Detecta problemas no vídeo (VFR, timestamps, áudio).
        Se `info` for fornecido (resultado de _obter_info_video), deriva sem ffprobe extra.
        """
        problemas = {"vfr": False, "timestamps": False, "audio_desync": False}

        if info is None:
            if shutil.which("ffprobe") is None:
                return problemas
            info = self._obter_info_video(arquivo)

        fps = info.get("fps")
        if fps is not None:
            if fps < 10 or fps > 120 or fps != int(fps):
                problemas["vfr"] = True

        if info.get("audio_codec") is None:
            problemas["audio_desync"] = True

        if problemas["vfr"] or problemas["audio_desync"]:
            problemas["timestamps"] = True

        return problemas

    def corrigir_video(
        self, arquivo_entrada: Path, arquivo_saida: Path,
        info: Dict = None, problemas: Dict = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Corrige problemas no vídeo usando FFmpeg com barra de progresso.
        Aceita `info` e `problemas` pré-calculados para evitar ffprobe redundante.
        """
        if info is None:
            info = self._obter_info_video(arquivo_entrada)

        duracao_total = info.get("duracao") or 100

        if problemas is None:
            problemas = self.detectar_problemas(arquivo_entrada, info)

        # Determina quais correções aplicar baseado nas configurações
        aplicar_vfr = self.corrigir_vfr and problemas["vfr"]
        aplicar_timestamps = self.corrigir_timestamps and problemas["timestamps"]
        aplicar_audio = self.corrigir_audio and problemas["audio_desync"]

        aplicar_correcoes = aplicar_vfr or aplicar_timestamps or aplicar_audio

        if not aplicar_correcoes:
            return False, "Nenhum problema detectado ou correções desabilitadas"

        if aplicar_correcoes:
            print(f"   🔍 Problemas detectados:")
            if aplicar_vfr:
                print(f"      ⚠️  Frame rate variável (VFR) - será corrigido")
            if aplicar_timestamps:
                print(f"      ⚠️  Problemas com timestamps - será corrigido")
            if aplicar_audio:
                print(f"      ⚠️  Possível dessincronia de áudio - será corrigido")

        # Comando FFmpeg base
        comando = [
            "ffmpeg",
            "-y",
        ]

        # Adiciona flags de correção de erros se necessário
        if aplicar_correcoes:
            comando.extend(
                [
                    "-err_detect",
                    "ignore_err",
                ]
            )

        comando.extend(
            [
                "-i",
                str(arquivo_entrada),
            ]
        )

        # Filtros de vídeo (para correção de VFR)
        filtros_video = []
        precisa_reencodar_video = False

        if aplicar_vfr:
            precisa_reencodar_video = True
            fps_alvo = info.get("fps", 30)
            if fps_alvo and fps_alvo > 0:
                fps_alvo = round(fps_alvo)
            else:
                fps_alvo = 30
            filtros_video.append(f"fps={fps_alvo}")

        # Configurações de codificação
        if not precisa_reencodar_video:
            # Se não precisa re-encodar vídeo, usa copy
            comando.extend(
                [
                    "-c:v",
                    "copy",
                ]
            )
        else:
            # Re-encoda com H.264 (correção de VFR)
            comando.extend(
                [
                    "-c:v",
                    "libx264",
                    "-crf",
                    "23",  # Qualidade padrão para correções
                    "-preset",
                    "medium",
                    "-threads",
                    str(self.threads),
                ]
            )

        # Aplica filtros de vídeo se houver (requer re-encodar)
        if filtros_video:
            comando.extend(["-filter:v", ",".join(filtros_video)])

        # Áudio com correções se necessário
        filtro_audio = "aresample=async=1" if aplicar_audio else None

        comando.extend(
            [
                "-c:a",
                "aac",
                "-b:a",
                "128k",
            ]
        )

        if filtro_audio:
            comando.extend(["-af", filtro_audio])

        # Flags adicionais para correção
        comando.extend(
            [
                "-movflags",
                "+faststart",
                "-pix_fmt",
                "yuv420p",
            ]
        )

        if aplicar_timestamps or aplicar_audio:
            # Flags para corrigir timestamps e problemas de sincronia
            comando.extend(
                [
                    "-fflags",
                    "+genpts+igndts",
                    "-max_muxing_queue_size",
                    "4096",
                ]
            )

        comando.extend(
            [
                "-progress",
                "pipe:1",
                str(arquivo_saida),
            ]
        )

        # Regex para capturar o tempo processado
        regex_tempo = re.compile(r"out_time=(\d{2}:\d{2}:\d{2}\.\d+)")

        # Captura stderr para diagnóstico de erros
        stderr_output = []
        stderr_lock = threading.Lock()

        def ler_stderr():
            """Thread para ler stderr sem bloquear."""
            nonlocal stderr_output
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

            # Inicia thread para ler stderr
            stderr_thread = threading.Thread(target=ler_stderr, daemon=True)
            stderr_thread.start()

            with ProgressBar(
                total=int(duracao_total),
                unit="s",
                desc=f"🔧 {arquivo_entrada.name[:20]}...",
            ).context() as pbar:
                tempo_anterior = 0.0

                # Lê stdout linha por linha
                while True:
                    linha = processo.stdout.readline()
                    if not linha:
                        # Verifica se o processo terminou
                        if processo.poll() is not None:
                            break
                        # Se não terminou mas não há mais linhas, aguarda um pouco
                        continue

                    match = regex_tempo.search(linha)
                    if match:
                        tempo_atual_str = match.group(1)
                        tempo_atual_seg = self._converter_tempo_para_segundos(
                            tempo_atual_str
                        )

                        # Limita ao total para evitar ultrapassar 100%
                        tempo_atual_seg = min(tempo_atual_seg, duracao_total)

                        incremento = tempo_atual_seg - tempo_anterior
                        if incremento > 0:
                            # Garante que não ultrapasse o total
                            if pbar.n + incremento > int(duracao_total):
                                incremento = int(duracao_total) - pbar.n

                            if incremento > 0:
                                pbar.update(incremento)
                            tempo_anterior = tempo_atual_seg

                # Garante que a barra chegue a 100% ao finalizar
                if pbar.n < int(duracao_total):
                    pbar.update(int(duracao_total) - pbar.n)

            # Espera o processo terminar completamente
            try:
                processo.wait(timeout=30)
            except subprocess.TimeoutExpired:
                # Se exceder o timeout, mata o processo
                try:
                    processo.kill()
                    processo.wait(timeout=2)
                except Exception:
                    pass
                return False, "FFmpeg excedeu o tempo limite de espera"

            # Aguarda thread de stderr terminar
            stderr_thread.join(timeout=2)

            # Obtém o código de retorno
            returncode = processo.returncode

            # Converte stderr para string
            with stderr_lock:
                stderr_text = "".join(stderr_output)

            # Código de retorno válido no Windows/Linux é geralmente 0-255
            if returncode is None:
                return False, "FFmpeg não retornou código de saída"

            if returncode < 0 or (returncode > 255 and returncode != 0xFFFFFFFF):
                # Tenta obter mais informações do stderr
                erro_msg = "FFmpeg foi interrompido ou terminou de forma anormal"
                if stderr_text:
                    # Pega as últimas linhas de erro do FFmpeg
                    linhas_erro = [
                        linha.strip()
                        for linha in stderr_text.split("\n")
                        if linha.strip()
                        and (
                            "error" in linha.lower()
                            or "failed" in linha.lower()
                            or "cannot" in linha.lower()
                        )
                    ]
                    if linhas_erro:
                        # Pega a última linha de erro relevante
                        erro_msg += f": {linhas_erro[-1][:200]}"
                return False, erro_msg

            if returncode == 0:
                return True, None
            else:
                # Código de erro válido do FFmpeg
                erro_msg = f"FFmpeg retornou código {returncode}"
                if stderr_text:
                    linhas_erro = [
                        linha.strip()
                        for linha in stderr_text.split("\n")
                        if linha.strip()
                        and (
                            "error" in linha.lower()
                            or "failed" in linha.lower()
                            or "cannot" in linha.lower()
                        )
                    ]
                    if linhas_erro:
                        erro_msg += f": {linhas_erro[-1][:200]}"
                return False, erro_msg

        except Exception as e:
            # Tenta obter informações do stderr se disponível
            erro_msg = f"Erro ao executar FFmpeg: {str(e)}"
            with stderr_lock:
                if stderr_output:
                    stderr_text = "".join(stderr_output)
                    linhas_erro = [
                        linha.strip()
                        for linha in stderr_text.split("\n")
                        if linha.strip()
                        and ("error" in linha.lower() or "failed" in linha.lower())
                    ]
                    if linhas_erro:
                        erro_msg += f" | FFmpeg: {linhas_erro[-1][:200]}"
            return False, erro_msg

    def processar(self, deletar_originais: bool = False) -> dict:
        """
        Processa todos os vídeos na pasta de entrada, corrigindo problemas.

        Args:
            deletar_originais: Se True, deleta os arquivos originais após processar.

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

        arquivos = [
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print("ℹ️  Nenhum vídeo encontrado.")
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        print(f"\n🔧 Iniciando correção de {len(arquivos)} vídeo(s)...")
        print(f"⚙️  Correções habilitadas:")
        print(f"   VFR: {'✅' if self.corrigir_vfr else '❌'}")
        print(f"   Timestamps: {'✅' if self.corrigir_timestamps else '❌'}")
        print(f"   Áudio: {'✅' if self.corrigir_audio else '❌'}")
        print(f"🔧 Controle de recursos:")
        print(
            f"   Threads: {self.threads} | Limite CPU: {self.limite_cpu:.0f}% | Limite Memória: {self.limite_memoria:.0f}%"
        )
        print("-" * 60)

        sucessos = 0
        falhas = 0
        pulados = 0

        # Processamento sequencial com informações detalhadas
        for i, arquivo_origem in enumerate(arquivos, 1):
            # Verifica recursos antes de processar
            if not verificar_recursos_disponiveis(self.limite_cpu, self.limite_memoria):
                print(
                    f"\n⏸️  Aguardando recursos disponíveis (CPU < {self.limite_cpu:.0f}%, Memória < {self.limite_memoria:.0f}%)..."
                )
                if not aguardar_recursos_disponiveis(
                    self.limite_cpu, self.limite_memoria, timeout=120.0
                ):
                    print("⚠️  Timeout aguardando recursos. Continuando com cautela...")

            arquivo_destino = pasta_saida / arquivo_origem.name

            # 1 ffprobe cobre info + detecção de problemas
            info_antes = self._obter_info_video(arquivo_origem)
            problemas = self.detectar_problemas(arquivo_origem, info_antes)

            # Verifica se há problemas para corrigir
            tem_problemas = False
            if self.corrigir_vfr and problemas["vfr"]:
                tem_problemas = True
            if self.corrigir_timestamps and problemas["timestamps"]:
                tem_problemas = True
            if self.corrigir_audio and problemas["audio_desync"]:
                tem_problemas = True

            if not tem_problemas:
                print(
                    f"\n[{i}/{len(arquivos)}] ⏭️  {arquivo_origem.name}: sem problemas detectados"
                )
                print(
                    f"   Info: {info_antes['width']}x{info_antes['height']} | "
                    f"{info_antes['codec']} | "
                    f"{info_antes['bitrate_total']:.0f}kbps"
                    if info_antes.get("bitrate_total")
                    else "N/A"
                )
                pulados += 1
                continue

            tamanho_original = arquivo_origem.stat().st_size / (1024 * 1024)

            print(f"\n[{i}/{len(arquivos)}] 🔧 {arquivo_origem.name}")
            print(
                f"   Antes: {info_antes['width']}x{info_antes['height']} | "
                f"{info_antes['codec']} | "
                f"{info_antes['bitrate_total']:.0f}kbps"
                if info_antes.get("bitrate_total")
                else "N/A"
            )

            sucesso, erro = self.corrigir_video(arquivo_origem, arquivo_destino, info_antes, problemas)

            if sucesso and arquivo_destino.exists():
                info_depois = self._obter_info_video(arquivo_destino)
                tamanho_novo = arquivo_destino.stat().st_size / (1024 * 1024)

                print(f"   ✅ Finalizado.")
                print(
                    f"   📊 Tamanho: {tamanho_original:.2f}MB -> {tamanho_novo:.2f}MB"
                )
                print(
                    f"   Depois: {info_depois['width']}x{info_depois['height']} | "
                    f"{info_depois['codec']} | "
                    f"{info_depois['bitrate_total']:.0f}kbps"
                    if info_depois.get("bitrate_total")
                    else "N/A"
                )

                if deletar_originais:
                    try:
                        arquivo_origem.unlink()
                        print("   🗑️  Original removido.")
                    except OSError:
                        pass
                sucessos += 1
            else:
                print(f"   ❌ Erro: {erro}")
                falhas += 1

            # Pausa entre processamentos para dar tempo ao sistema se recuperar
            if i < len(arquivos):  # Não pausa após o último vídeo
                pausar_entre_processamentos(self.pausa_entre_videos)

        print("\n" + "=" * 60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        if pulados > 0:
            print(f"⏭️  Pulados (sem problemas): {pulados}")
        print(f"❌ Falhas: {falhas}")
        print("-" * 60)
        print("✨ Processo finalizado!")

        return {"sucessos": sucessos, "falhas": falhas, "pulados": pulados}

