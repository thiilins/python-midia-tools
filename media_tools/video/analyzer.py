"""
Analisador de mídia — inventário de pasta com estimativas de compressão.
Usa ffprobe para extrair codec, resolução, FPS, bitrate, duração e tamanho.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from ..common.paths import obter_pastas_entrada_saida
from ..common.validators import verificar_ffmpeg


def _formatar_tamanho(bytes_: float) -> str:
    """Formata bytes para GB/MB/KB legível."""
    if bytes_ >= 1024 ** 3:
        return f"{bytes_ / 1024 ** 3:.1f}GB"
    elif bytes_ >= 1024 ** 2:
        return f"{bytes_ / 1024 ** 2:.0f}MB"
    elif bytes_ >= 1024:
        return f"{bytes_ / 1024:.0f}KB"
    return f"{bytes_:.0f}B"


def _formatar_duracao(segundos: float) -> str:
    """Formata segundos para Xh00m ou Xm00s."""
    if segundos <= 0:
        return "?"
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    if h > 0:
        return f"{h}h{m:02d}m"
    return f"{m}m{s:02d}s"


class AnalisadorMidia:
    """
    Analisa uma pasta de vídeos e exibe tabela com informações técnicas
    e estimativa de tamanho pós-compressão H.265 stream_720p.

    Útil para decidir quais arquivos comprimir e qual preset usar.
    """

    EXTENSOES_VIDEO = {".mp4", ".m4v", ".mov", ".webm", ".avi", ".mkv"}

    # Bitrate médio estimado para stream_720p (vídeo ~700k + áudio ~96k)
    BITRATE_STREAM_720P_BPS = 800_000

    def __init__(self, pasta: Path = None):
        if pasta is None:
            entrada, _ = obter_pastas_entrada_saida("videos")
            self.pasta = Path(entrada)
        else:
            self.pasta = Path(pasta)

    def _obter_info_video(self, arquivo: Path) -> Optional[Dict]:
        """Obtém informações completas do vídeo via ffprobe (1 chamada)."""
        comando = [
            "ffprobe", "-v", "error",
            "-print_format", "json",
            "-show_streams", "-show_format",
            str(arquivo),
        ]
        try:
            resultado = subprocess.run(
                comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=30
            )
            if resultado.returncode != 0:
                return None
            dados = json.loads(resultado.stdout)
        except Exception:
            return None

        info: Dict = {
            "nome": arquivo.name,
            "tamanho_bytes": arquivo.stat().st_size,
            "codec": "?",
            "resolucao": "?",
            "largura": 0,
            "altura": 0,
            "fps": "?",
            "fps_valor": 0.0,
            "bitrate_kbps": 0,
            "duracao_s": 0.0,
            "audio_codec": "?",
        }

        fmt = dados.get("format", {})
        try:
            info["duracao_s"] = float(fmt.get("duration", 0))
        except (ValueError, TypeError):
            pass

        bitrate = fmt.get("bit_rate")
        if bitrate:
            try:
                info["bitrate_kbps"] = int(bitrate) // 1000
            except (ValueError, TypeError):
                pass

        for stream in dados.get("streams", []):
            codec_type = stream.get("codec_type", "")
            if codec_type == "video":
                info["codec"] = stream.get("codec_name", "?")
                w = stream.get("width", 0)
                h = stream.get("height", 0)
                if w and h:
                    info["largura"] = w
                    info["altura"] = h
                    info["resolucao"] = f"{w}x{h}"
                fps_str = stream.get("r_frame_rate", "0/1")
                try:
                    num, den = fps_str.split("/")
                    fps_val = float(num) / float(den) if float(den) else 0.0
                    info["fps_valor"] = fps_val
                    info["fps"] = f"{fps_val:.0f}" if fps_val == int(fps_val) else f"{fps_val:.1f}"
                except Exception:
                    pass
            elif codec_type == "audio" and info["audio_codec"] == "?":
                info["audio_codec"] = stream.get("codec_name", "?")

        return info

    def _estimar_compressao(self, info: Dict, preset: str = "stream_720p") -> str:
        """
        Estima tamanho pós-compressão baseado no bitrate médio do preset.
        Leva em conta redução de resolução para 720p quando aplicável.
        """
        dur = info["duracao_s"]
        if dur <= 0:
            return "?"

        # Bitrates médios por preset (vídeo + áudio)
        bitrates = {
            "stream_720p": 800_000,   # 700k vídeo + 96k áudio
            "stream_540p": 500_000,   # 404k vídeo + 96k áudio
            "stream_480p": 300_000,   # 204k vídeo + 96k áudio
        }
        bitrate_bps = bitrates.get(preset, 800_000)
        estimado_bytes = dur * bitrate_bps / 8
        original = info["tamanho_bytes"]
        if original <= 0:
            return "?"
        reducao = (1 - estimado_bytes / original) * 100
        sinal = "-" if reducao >= 0 else "+"
        return f"~{_formatar_tamanho(estimado_bytes)} ({sinal}{abs(reducao):.0f}%)"

    def _recomendar_preset(self, info: Dict) -> str:
        """Recomenda preset baseado no codec, FPS e resolução."""
        fps = info.get("fps_valor", 0)
        altura = info.get("altura", 0)
        codec = info.get("codec", "?")

        # Já está em H.265 e 720p ou menos
        if codec == "hevc" and altura <= 720:
            return "já otimizado"

        if fps > 50:
            return "converter-fps → stream_720p"
        if altura > 1080:
            return "stream_720p"
        if altura > 720:
            return "stream_720p"
        return "stream_720p"

    def analisar(self) -> List[Dict]:
        """
        Analisa todos os vídeos da pasta e retorna lista de informações.

        Returns:
            Lista de dicts com informações de cada arquivo.
        """
        pasta = self.pasta.resolve()
        if not pasta.exists():
            return []

        arquivos = sorted([
            f for f in pasta.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VIDEO
        ])

        infos = []
        for arq in arquivos:
            info = self._obter_info_video(arq)
            if info:
                infos.append(info)

        return infos

    def processar(self) -> dict:
        """
        Analisa pasta e imprime relatório completo no terminal.

        Returns:
            dict: {"arquivos": N, "total_bytes": N, "total_duracao_s": N}
        """
        if not verificar_ffmpeg():
            return {}

        pasta = self.pasta.resolve()
        if not pasta.exists():
            print(f"❌ Pasta não encontrada: {pasta}")
            return {}

        arquivos = sorted([
            f for f in pasta.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VIDEO
        ])

        if not arquivos:
            print(f"ℹ️  Nenhum vídeo encontrado em {pasta}")
            return {}

        print(f"\n⏳ Analisando {len(arquivos)} vídeo(s)...")

        infos = []
        for arq in arquivos:
            info = self._obter_info_video(arq)
            if info:
                infos.append(info)
                print(f"  ✓ {arq.name}")
            else:
                print(f"  ✗ {arq.name} (falha ao ler)")

        if not infos:
            print("❌ Nenhum arquivo analisado com sucesso.")
            return {}

        total_bytes = sum(i["tamanho_bytes"] for i in infos)
        total_duracao = sum(i["duracao_s"] for i in infos)

        # --- Tabela principal ---
        print("\n" + "=" * 110)
        print(f"📊  INVENTÁRIO DE MÍDIA — {pasta}")
        print("=" * 110)

        col_nome = 32
        print(
            f"{'Arquivo':<{col_nome}} {'Codec':<7} {'Resolução':<11} "
            f"{'FPS':<5} {'Bitrate':<9} {'Duração':<9} {'Tamanho':<9} "
            f"{'H.265 stream_720p':<18} Recomendação"
        )
        print("-" * 110)

        for info in infos:
            nome = info["nome"]
            if len(nome) > col_nome:
                nome = nome[: col_nome - 1] + "…"

            estimativa = self._estimar_compressao(info)
            recomendacao = self._recomendar_preset(info)
            bitrate_str = f"{info['bitrate_kbps']}k" if info["bitrate_kbps"] else "?"

            print(
                f"{nome:<{col_nome}} "
                f"{info['codec']:<7} "
                f"{info['resolucao']:<11} "
                f"{info['fps']:<5} "
                f"{bitrate_str:<9} "
                f"{_formatar_duracao(info['duracao_s']):<9} "
                f"{_formatar_tamanho(info['tamanho_bytes']):<9} "
                f"{estimativa:<18} "
                f"{recomendacao}"
            )

        print("=" * 110)
        print(
            f"\n📦 Total: {len(infos)} arquivo(s) | "
            f"{_formatar_tamanho(total_bytes)} | "
            f"{_formatar_duracao(total_duracao)}"
        )

        # Estimativa total pós-compressão
        if total_duracao > 0:
            estimado_total = total_duracao * self.BITRATE_STREAM_720P_BPS / 8
            reducao_total = (1 - estimado_total / total_bytes) * 100 if total_bytes > 0 else 0
            print(
                f"💡 Estimativa pós H.265 stream_720p: "
                f"~{_formatar_tamanho(estimado_total)} "
                f"({reducao_total:.0f}% menor)"
            )

        print("\nComandos:")
        print("  python otimizador-compressor-video.py --preset stream_720p  # compressão")
        print("  python converter-fps.py                                      # reduzir 60→30fps primeiro")
        print("  python cortar-video.py                                       # extrair clips antes")
        print("=" * 110)

        return {
            "arquivos": len(infos),
            "total_bytes": total_bytes,
            "total_duracao_s": total_duracao,
        }
