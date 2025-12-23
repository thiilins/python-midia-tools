"""
Estabilizador de vídeos - Corrige vídeos tremidos.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg


class EstabilizadorVideo:
    """
    Classe para estabilizar vídeos tremidos.
    """

    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov", ".webm", ".avi"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        correcao_rotacao: bool = True,
    ):
        """
        Inicializa o estabilizador.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            correcao_rotacao: Se True, corrige rotação automática.
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.correcao_rotacao = correcao_rotacao

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

    def _estabilizar_video(self, arquivo_entrada: Path, arquivo_saida: Path) -> bool:
        """
        Estabiliza um vídeo usando FFmpeg.

        Args:
            arquivo_entrada: Caminho do vídeo de entrada.
            arquivo_saida: Caminho do vídeo de saída.

        Returns:
            bool: True se a estabilização foi bem-sucedida.
        """
        duracao = self._obter_duracao(arquivo_entrada)
        if duracao == 0:
            duracao = 100  # Fallback

        # Passo 1: Analisa e gera arquivo de transformação
        arquivo_trf = arquivo_saida.with_suffix(".trf")

        comando_analise = [
            "ffmpeg",
            "-i",
            str(arquivo_entrada),
            "-vf",
            "vidstabdetect=shakiness=10:accuracy=15:result=" + str(arquivo_trf),
            "-f",
            "null",
            "-",
        ]

        try:
            print("   🔍 Analisando movimento...")
            resultado = subprocess.run(
                comando_analise,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3600,
            )

            if resultado.returncode != 0:
                return False

            # Passo 2: Aplica estabilização
            print("   🎬 Aplicando estabilização...")

            filtros = ["vidstabtransform=input=" + str(arquivo_trf) + ":smoothing=10"]

            # Adiciona correção de rotação se solicitado
            if self.correcao_rotacao:
                filtros.append("deshake")

            comando_estabilizar = [
                "ffmpeg",
                "-y",
                "-i",
                str(arquivo_entrada),
                "-vf",
                ",".join(filtros),
                "-c:a",
                "copy",  # Copia áudio sem re-encodar
                str(arquivo_saida),
            ]

            with ProgressBar(
                total=int(duracao), unit="s", desc="Estabilizando"
            ).context() as pbar:
                processo = subprocess.Popen(
                    comando_estabilizar,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                # Simula progresso (FFmpeg não fornece progresso fácil para estabilização)
                import time
                tempo_inicio = time.time()
                while processo.poll() is None:
                    tempo_decorrido = time.time() - tempo_inicio
                    if tempo_decorrido < duracao:
                        pbar.update(int(tempo_decorrido) - pbar.n)
                    time.sleep(0.5)

                pbar.update(int(duracao) - pbar.n)

            # Remove arquivo temporário
            if arquivo_trf.exists():
                arquivo_trf.unlink()

            return processo.returncode == 0 and arquivo_saida.exists()

        except Exception as e:
            print(f"   ❌ Erro: {e}")
            if arquivo_trf.exists():
                arquivo_trf.unlink()
            return False

    def processar(self) -> dict:
        """
        Processa todos os vídeos na pasta de entrada.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not verificar_ffmpeg():
            return {"sucessos": 0, "falhas": 0}

        # Verifica se vidstab está disponível
        resultado = subprocess.run(
            ["ffmpeg", "-filters"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "vidstab" not in resultado.stdout and "vidstab" not in resultado.stderr:
            print("⚠️  AVISO: vidstab não está disponível no FFmpeg.")
            print("   A estabilização requer FFmpeg compilado com libvidstab.")
            print("   Continuando com estabilização básica...")

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

        print(f"🚀 Estabilizando {len(arquivos)} vídeo(s)...")
        print(f"⚙️  Correção de rotação: {'Sim' if self.correcao_rotacao else 'Não'}")
        print("-" * 60)

        sucessos = 0
        falhas = 0

        for i, arquivo in enumerate(arquivos, 1):
            nome_saida = arquivo.stem + "_estabilizado" + arquivo.suffix
            arquivo_saida = pasta_saida / nome_saida

            print(f"\n[{i}/{len(arquivos)}] 📹 {arquivo.name}")

            if self._estabilizar_video(arquivo, arquivo_saida):
                tamanho_mb = arquivo_saida.stat().st_size / (1024 * 1024)
                print(f"   ✅ Estabilizado! Tamanho: {tamanho_mb:.2f} MB")
                sucessos += 1
            else:
                print(f"   ❌ Erro ao estabilizar")
                falhas += 1

        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print("-" * 60)

        return {"sucessos": sucessos, "falhas": falhas}


