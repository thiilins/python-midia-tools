"""
Removedor de fundo de imagens.
"""

import shutil
from pathlib import Path
from typing import Optional

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar


class RemovedorFundo:
    """
    Classe para remover fundo de imagens.
    """

    EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
    ):
        """
        Inicializa o removedor.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("imagens")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or (Path(saida).parent / "sem_fundo")
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

    def _verificar_rembg(self) -> bool:
        """Verifica se rembg está disponível."""
        try:
            import rembg
            return True
        except ImportError:
            return False

    def _remover_fundo(self, caminho_entrada: Path, caminho_saida: Path) -> bool:
        """
        Remove fundo de uma imagem.

        Args:
            caminho_entrada: Caminho da imagem de entrada.
            caminho_saida: Caminho da imagem de saída (PNG com transparência).

        Returns:
            bool: True se a remoção foi bem-sucedida.
        """
        try:
            from rembg import remove
            from PIL import Image

            # Lê a imagem
            with open(caminho_entrada, "rb") as f:
                input_data = f.read()

            # Remove fundo
            output_data = remove(input_data)

            # Salva como PNG com transparência
            nome_saida = caminho_saida.stem + ".png"
            caminho_saida_png = caminho_saida.parent / nome_saida

            with open(caminho_saida_png, "wb") as f:
                f.write(output_data)

            return caminho_saida_png.exists()
        except ImportError:
            return False
        except Exception as e:
            print(f"   ⚠️  Erro: {e}")
            return False

    def processar(self) -> dict:
        """
        Processa todas as imagens na pasta de entrada.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not self._verificar_rembg():
            print("❌ ERRO: rembg não está instalado.")
            print("   Instale: pip install rembg")
            print("   Nota: A primeira execução baixará o modelo (~170MB)")
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
            print(f"ℹ️  Nenhuma imagem encontrada em {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0}

        print(f"🚀 Removendo fundo de {len(arquivos)} imagem(ns)...")
        print("   (A primeira execução pode demorar para baixar o modelo)")
        print("-" * 60)

        sucessos = 0
        falhas = 0

        with ProgressBar(
            total=len(arquivos), desc="Removendo fundo", unit="img"
        ).context() as pbar:
            for arquivo in arquivos:
                nome_saida = arquivo.stem + ".png"
                arquivo_saida = pasta_saida / nome_saida

                if self._remover_fundo(arquivo, arquivo_saida):
                    tamanho_kb = arquivo_saida.stat().st_size / 1024
                    print(f"\n✅ {arquivo.name} -> {nome_saida} ({tamanho_kb:.1f} KB)")
                    sucessos += 1
                else:
                    print(f"\n❌ Erro ao processar {arquivo.name}")
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

