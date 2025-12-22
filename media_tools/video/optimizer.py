"""
Otimizador de vídeos (MP4, M4V, MOV).
"""

import json
import multiprocessing
import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg


class OtimizadorVideo:
    """
    Classe para otimizar vídeos usando FFmpeg.
    """

    # Extensões suportadas
    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov"}

    # Configurações padrão
    CRF_VALUE = "23"
    PRESET_VALUE = "medium"

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        crf: str = None,
        preset: str = None,
    ):
        """
        Inicializa o otimizador.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            crf: Valor CRF para qualidade (None = padrão).
            preset: Preset de velocidade (None = padrão).
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.crf = crf or self.CRF_VALUE
        self.preset = preset or self.PRESET_VALUE

    def _obter_info_video(self, arquivo: Path) -> Dict:
        """
        Obtém informações detalhadas do vídeo usando ffprobe.

        Args:
            arquivo: Caminho do arquivo de vídeo.

        Returns:
            dict: Informações do vídeo (codec, resolução, bitrate, duração, etc.)
        """
        comando = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,bit_rate,r_frame_rate",
            "-show_entries",
            "format=duration,bit_rate,size",
            "-of",
            "json",
            str(arquivo),
        ]

        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=10,
            )
            data = json.loads(resultado.stdout)

            info = {
                "codec": None,
                "width": None,
                "height": None,
                "bitrate_video": None,
                "bitrate_total": None,
                "fps": None,
                "duracao": None,
                "tamanho": None,
            }

            # Extrai informações do stream de vídeo
            if "streams" in data and len(data["streams"]) > 0:
                stream = data["streams"][0]
                info["codec"] = stream.get("codec_name", "unknown")
                info["width"] = stream.get("width", 0)
                info["height"] = stream.get("height", 0)
                info["bitrate_video"] = stream.get("bit_rate")
                if info["bitrate_video"]:
                    info["bitrate_video"] = int(info["bitrate_video"]) / 1000  # kbps

                # Calcula FPS
                r_frame_rate = stream.get("r_frame_rate", "")
                if r_frame_rate and "/" in r_frame_rate:
                    num, den = map(int, r_frame_rate.split("/"))
                    if den > 0:
                        info["fps"] = round(num / den, 2)

            # Extrai informações do formato
            if "format" in data:
                format_info = data["format"]
                info["duracao"] = float(format_info.get("duration", 0))
                info["bitrate_total"] = format_info.get("bit_rate")
                if info["bitrate_total"]:
                    info["bitrate_total"] = int(info["bitrate_total"]) / 1000  # kbps
                info["tamanho"] = int(format_info.get("size", 0))

            return info
        except Exception as e:
            return {
                "codec": "unknown",
                "width": 0,
                "height": 0,
                "bitrate_video": None,
                "bitrate_total": None,
                "fps": None,
                "duracao": 0,
                "tamanho": 0,
            }

    def _ja_otimizado(self, info_original: Dict, crf_target: str) -> bool:
        """
        Verifica se o vídeo já está otimizado.

        Args:
            info_original: Informações do vídeo original.
            crf_target: CRF alvo.

        Returns:
            bool: True se já está otimizado.
        """
        # Se já é H.264 e tem resolução razoável, pode estar otimizado
        if info_original["codec"] == "h264":
            # Verifica se tem bitrate baixo (indicando compressão)
            if info_original["bitrate_total"]:
                # Bitrate muito alto pode indicar que não foi otimizado
                if info_original["bitrate_total"] > 5000:  # > 5 Mbps
                    return False
            return True
        return False

    def _obter_duracao_video(self, arquivo: Path) -> float:
        """
        Obtém a duração do vídeo em segundos usando ffprobe.

        Args:
            arquivo: Caminho do arquivo de vídeo.

        Returns:
            float: Duração em segundos, ou 0.0 se não conseguir obter.
        """
        comando = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(arquivo),
        ]
        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=10,
            )
            return float(resultado.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return 0.0

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

    def _converter_video(
        self, arquivo_entrada: Path, arquivo_saida: Path
    ) -> tuple[bool, Optional[str]]:
        """
        Converte o vídeo usando FFmpeg com barra de progresso.

        Args:
            arquivo_entrada: Caminho do arquivo de entrada.
            arquivo_saida: Caminho do arquivo de saída.

        Returns:
            Tuple[bool, Optional[str]]: (sucesso, mensagem_erro)
        """
        duracao_total = self._obter_duracao_video(arquivo_entrada)

        if duracao_total == 0:
            duracao_total = 100  # Fallback

        # Comando FFmpeg
        comando = [
            "ffmpeg",
            "-y",
            "-i",
            str(arquivo_entrada),
            "-c:v",
            "libx264",
            "-crf",
            self.crf,
            "-preset",
            self.preset,
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            "-pix_fmt",
            "yuv420p",
            "-progress",
            "pipe:1",
            str(arquivo_saida),
        ]

        # Regex para capturar o tempo processado
        regex_tempo = re.compile(r"out_time=(\d{2}:\d{2}:\d{2}\.\d+)")

        try:
            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                universal_newlines=True,
            )

            with ProgressBar(
                total=int(duracao_total),
                unit="s",
                desc=f"🎬 {arquivo_entrada.name[:20]}...",
            ).context() as pbar:
                tempo_anterior = 0.0

                while True:
                    linha = processo.stdout.readline()
                    if not linha and processo.poll() is not None:
                        break

                    match = regex_tempo.search(linha)
                    if match:
                        tempo_atual_str = match.group(1)
                        tempo_atual_seg = self._converter_tempo_para_segundos(
                            tempo_atual_str
                        )

                        incremento = tempo_atual_seg - tempo_anterior
                        if incremento > 0:
                            pbar.update(incremento)
                            tempo_anterior = tempo_atual_seg

            if processo.returncode == 0:
                return True, None
            else:
                return False, f"FFmpeg retornou código {processo.returncode}"

        except Exception as e:
            return False, str(e)

    def processar(self, deletar_originais: bool = True) -> dict:
        """
        Processa todos os vídeos na pasta de entrada.

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

        print(f"\n🚀 Iniciando otimização de {len(arquivos)} vídeo(s)...")
        print(f"⚙️  Configuração: CRF {self.crf} | Preset {self.preset}")
        print("-" * 60)

        sucessos = 0
        falhas = 0
        pulados = 0

        # Processamento sequencial com informações detalhadas
        for i, arquivo_origem in enumerate(arquivos, 1):
            arquivo_destino = pasta_saida / arquivo_origem.name

            # Obtém informações antes
            info_antes = self._obter_info_video(arquivo_origem)

            # Verifica se já está otimizado
            if self._ja_otimizado(info_antes, self.crf):
                print(f"\n[{i}/{len(arquivos)}] ⏭️  {arquivo_origem.name}: já otimizado")
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

            print(f"\n[{i}/{len(arquivos)}] 📹 {arquivo_origem.name}")
            print(
                f"   Antes: {info_antes['width']}x{info_antes['height']} | "
                f"{info_antes['codec']} | "
                f"{info_antes['bitrate_total']:.0f}kbps"
                if info_antes.get("bitrate_total")
                else "N/A"
            )

            sucesso, erro = self._converter_video(arquivo_origem, arquivo_destino)

            if sucesso and arquivo_destino.exists():
                info_depois = self._obter_info_video(arquivo_destino)
                tamanho_novo = arquivo_destino.stat().st_size / (1024 * 1024)
                reducao = 100 - (tamanho_novo / tamanho_original * 100)

                print(f"   ✅ Finalizado.")
                print(
                    f"   📊 Redução: {reducao:.1f}% ({tamanho_original:.2f}MB -> {tamanho_novo:.2f}MB)"
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

        print("\n" + "=" * 60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        if pulados > 0:
            print(f"⏭️  Pulados (já otimizados): {pulados}")
        print(f"❌ Falhas: {falhas}")
        print("-" * 60)
        print("✨ Processo finalizado!")

        return {"sucessos": sucessos, "falhas": falhas, "pulados": pulados}
