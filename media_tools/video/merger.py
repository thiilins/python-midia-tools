"""
Merger de vídeos - Concatena múltiplos vídeos.
"""

import subprocess
from pathlib import Path
from typing import List

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg


class MergerVideos:
    """
    Classe para concatenar múltiplos vídeos.
    """

    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov", ".webm"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        nome_saida: str = "video_merged.mp4",
    ):
        """
        Inicializa o merger.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            nome_saida: Nome do arquivo de saída.
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.nome_saida = nome_saida

    def _criar_lista_concat(self, arquivos: List[Path], lista_path: Path) -> bool:
        """
        Cria arquivo de lista para concatenação do FFmpeg.

        Args:
            arquivos: Lista de arquivos de vídeo.
            lista_path: Caminho do arquivo de lista.

        Returns:
            bool: True se criado com sucesso.
        """
        try:
            with open(lista_path, "w", encoding="utf-8") as f:
                for arquivo in arquivos:
                    f.write(f"file '{arquivo.resolve()}'\n")
            return True
        except Exception:
            return False

    def processar(self) -> dict:
        """
        Processa e concatena todos os vídeos na pasta de entrada.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not verificar_ffmpeg():
            return {"sucesso": False, "arquivo_saida": None}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"sucesso": False, "arquivo_saida": None}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = sorted([
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ])

        if len(arquivos) < 2:
            print("ℹ️  É necessário pelo menos 2 vídeos para concatenar.")
            return {"sucesso": False, "arquivo_saida": None}

        print(f"🚀 Concatenando {len(arquivos)} vídeo(s)...")
        print("-" * 60)

        # Cria arquivo de lista temporário
        lista_path = pasta_saida / "concat_list.txt"
        if not self._criar_lista_concat(arquivos, lista_path):
            print("❌ Erro ao criar lista de concatenação.")
            return {"sucesso": False, "arquivo_saida": None}

        arquivo_saida = pasta_saida / self.nome_saida

        # Comando FFmpeg para concatenação
        comando = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lista_path),
            "-c",
            "copy",  # Copia streams sem re-encodar (mais rápido)
            str(arquivo_saida),
        ]

        try:
            print("⏳ Processando concatenação...")
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=7200,  # 2 horas
            )

            # Remove arquivo de lista temporário
            if lista_path.exists():
                lista_path.unlink()

            if resultado.returncode == 0 and arquivo_saida.exists():
                tamanho_mb = arquivo_saida.stat().st_size / (1024 * 1024)
                print(f"\n✅ Vídeo concatenado com sucesso!")
                print(f"   📁 Arquivo: {arquivo_saida.name}")
                print(f"   💾 Tamanho: {tamanho_mb:.2f} MB")
                return {"sucesso": True, "arquivo_saida": str(arquivo_saida)}
            else:
                print(f"\n❌ Erro ao concatenar vídeos.")
                if resultado.stderr:
                    print(f"   Detalhes: {resultado.stderr[-200:]}")
                return {"sucesso": False, "arquivo_saida": None}

        except subprocess.TimeoutExpired:
            print("\n❌ Timeout ao concatenar vídeos.")
            return {"sucesso": False, "arquivo_saida": None}
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            return {"sucesso": False, "arquivo_saida": None}

