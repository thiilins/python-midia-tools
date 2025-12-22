"""
Extrator de áudio e thumbnails de vídeos.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, List

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg


class ExtratorAudio:
    """
    Classe para extrair áudio de vídeos.
    """

    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov", ".webm", ".avi", ".mkv"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        formato: str = "mp3",
        qualidade: str = "192k",
    ):
        """
        Inicializa o extrator.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            formato: Formato de saída (mp3, aac, ogg, wav).
            qualidade: Qualidade do áudio (bitrate).
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or (Path(saida).parent / "audio")
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.formato = formato.lower()
        self.qualidade = qualidade

    def _extrair_audio(self, arquivo_video: Path, arquivo_audio: Path) -> bool:
        """
        Extrai áudio de um vídeo.

        Args:
            arquivo_video: Caminho do vídeo.
            arquivo_audio: Caminho do arquivo de áudio de saída.

        Returns:
            bool: True se a extração foi bem-sucedida.
        """
        # Mapeia formato para codec
        codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "ogg": "libvorbis",
            "wav": "pcm_s16le",
        }

        codec = codec_map.get(self.formato, "libmp3lame")

        comando = [
            "ffmpeg",
            "-y",
            "-i",
            str(arquivo_video),
            "-vn",  # Sem vídeo
            "-acodec",
            codec,
            "-ab",
            self.qualidade,
            "-ar",
            "44100",  # Sample rate
            str(arquivo_audio),
        ]

        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3600,  # 1 hora
            )
            return resultado.returncode == 0 and arquivo_audio.exists()
        except Exception:
            return False

    def processar(self) -> dict:
        """
        Processa todos os vídeos na pasta de entrada.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not verificar_ffmpeg():
            return {"sucessos": 0, "falhas": 0}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"sucessos": 0, "falhas": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = [
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print(f"ℹ️  Nenhum vídeo encontrado em {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0}

        print(f"🚀 Extraindo áudio de {len(arquivos)} vídeo(s)...")
        print(f"⚙️  Formato: {self.formato.upper()} | Qualidade: {self.qualidade}")
        print("-" * 60)

        sucessos = 0
        falhas = 0

        with ProgressBar(
            total=len(arquivos), desc="Extraindo", unit="vídeo"
        ).context() as pbar:
            for arquivo in arquivos:
                nome_audio = arquivo.stem + f".{self.formato}"
                arquivo_audio = pasta_saida / nome_audio

                if self._extrair_audio(arquivo, arquivo_audio):
                    tamanho_mb = arquivo_audio.stat().st_size / (1024 * 1024)
                    print(f"\n✅ {arquivo.name} -> {nome_audio} ({tamanho_mb:.2f} MB)")
                    sucessos += 1
                else:
                    print(f"\n❌ Erro ao extrair áudio de {arquivo.name}")
                    falhas += 1

                pbar.update(1)

        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📁 Arquivos salvos em: {pasta_saida}")
        print("-" * 60)

        return {"sucessos": sucessos, "falhas": falhas}


class ExtratorThumbnails:
    """
    Classe para extrair thumbnails de vídeos.
    """

    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov", ".webm", ".avi", ".mkv"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        quantidade: int = 1,
        tamanho: str = "320x240",
    ):
        """
        Inicializa o extrator.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            quantidade: Número de thumbnails por vídeo.
            tamanho: Tamanho das thumbnails (ex: "320x240").
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or (Path(saida).parent / "thumbnails")
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.quantidade = quantidade
        self.tamanho = tamanho

    def _obter_duracao(self, arquivo: Path) -> float:
        """Obtém duração do vídeo."""
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
                comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
            )
            return float(resultado.stdout.strip())
        except Exception:
            return 0.0

    def _extrair_thumbnails(self, arquivo_video: Path) -> int:
        """
        Extrai thumbnails de um vídeo.

        Args:
            arquivo_video: Caminho do vídeo.

        Returns:
            int: Número de thumbnails extraídas com sucesso.
        """
        duracao = self._obter_duracao(arquivo_video)
        if duracao == 0:
            return 0

        sucessos = 0
        intervalo = duracao / (self.quantidade + 1) if self.quantidade > 1 else duracao / 2

        for i in range(1, self.quantidade + 1):
            tempo = intervalo * i
            nome_thumb = f"{arquivo_video.stem}_thumb_{i:02d}.jpg"
            arquivo_thumb = self.pasta_saida / nome_thumb

            comando = [
                "ffmpeg",
                "-y",
                "-ss",
                str(tempo),
                "-i",
                str(arquivo_video),
                "-vframes",
                "1",
                "-vf",
                f"scale={self.tamanho}",
                str(arquivo_thumb),
            ]

            try:
                resultado = subprocess.run(
                    comando,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                )
                if resultado.returncode == 0 and arquivo_thumb.exists():
                    sucessos += 1
            except Exception:
                pass

        return sucessos

    def processar(self) -> dict:
        """
        Processa todos os vídeos na pasta de entrada.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not verificar_ffmpeg():
            return {"sucessos": 0, "falhas": 0, "thumbnails": 0}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"sucessos": 0, "falhas": 0, "thumbnails": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = [
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print(f"ℹ️  Nenhum vídeo encontrado em {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0, "thumbnails": 0}

        print(f"🚀 Extraindo thumbnails de {len(arquivos)} vídeo(s)...")
        print(f"⚙️  Quantidade: {self.quantidade} por vídeo | Tamanho: {self.tamanho}")
        print("-" * 60)

        sucessos = 0
        falhas = 0
        total_thumbnails = 0

        with ProgressBar(
            total=len(arquivos), desc="Extraindo", unit="vídeo"
        ).context() as pbar:
            for arquivo in arquivos:
                thumbs = self._extrair_thumbnails(arquivo)
                if thumbs > 0:
                    print(f"\n✅ {arquivo.name}: {thumbs} thumbnail(s) extraída(s)")
                    sucessos += 1
                    total_thumbnails += thumbs
                else:
                    print(f"\n❌ Erro ao extrair thumbnails de {arquivo.name}")
                    falhas += 1

                pbar.update(1)

        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"🖼️  Total de thumbnails: {total_thumbnails}")
        print(f"📁 Arquivos salvos em: {pasta_saida}")
        print("-" * 60)

        return {"sucessos": sucessos, "falhas": falhas, "thumbnails": total_thumbnails}

