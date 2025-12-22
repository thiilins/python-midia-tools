"""
OCR de imagens - Detecção de texto legível.
"""

from pathlib import Path
from typing import Dict, Optional

from ..common.paths import obter_pastas_entrada_saida
from ..common.progress import ProgressBar


class OCRImagens:
    """
    Classe para detectar texto em imagens usando OCR.
    """

    EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

    def __init__(
        self,
        pasta_origem: Path = None,
        pasta_com_texto: Path = None,
        pasta_sem_texto: Path = None,
    ):
        """
        Inicializa o OCR.

        Args:
            pasta_origem: Pasta com imagens para analisar (None = padrão).
            pasta_com_texto: Pasta para imagens com texto (None = padrão).
            pasta_sem_texto: Pasta para imagens sem texto (None = padrão).
        """
        if pasta_origem is None:
            entrada, _ = obter_pastas_entrada_saida("imagens")
            self.pasta_origem = entrada
        else:
            self.pasta_origem = pasta_origem

        if pasta_com_texto is None or pasta_sem_texto is None:
            from ..common.paths import obter_diretorio_base

            base = obter_diretorio_base()
            self.pasta_com_texto = pasta_com_texto or (base / "saida" / "com_texto")
            self.pasta_sem_texto = pasta_sem_texto or (base / "saida" / "sem_texto")
        else:
            self.pasta_com_texto = pasta_com_texto
            self.pasta_sem_texto = pasta_sem_texto

    def _verificar_tesseract(self) -> bool:
        """Verifica se Tesseract está disponível."""
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def _analisar_imagem(self, caminho: Path) -> Dict:
        """
        Analisa imagem usando OCR.

        Args:
            caminho: Caminho da imagem.

        Returns:
            dict: Resultado da análise.
        """
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(caminho)

            # Extrai texto
            texto = pytesseract.image_to_string(img, lang="por+eng")

            # Verifica se há texto significativo (mais de 10 caracteres)
            texto_limpo = "".join(texto.split())
            tem_texto = len(texto_limpo) > 10

            # Calcula confiança média (se disponível)
            try:
                dados = pytesseract.image_to_data(
                    img, output_type=pytesseract.Output.DICT
                )
                confiancas = [int(c) for c in dados["conf"] if int(c) > 0]
                confianca_media = sum(confiancas) / len(confiancas) if confiancas else 0
            except Exception:
                confianca_media = 0

            return {
                "tem_texto": tem_texto,
                "texto": texto[:100] if texto else "",  # Primeiros 100 caracteres
                "confianca": confianca_media,
                "tamanho_texto": len(texto_limpo),
            }
        except ImportError:
            return {
                "tem_texto": False,
                "texto": "",
                "confianca": 0,
                "tamanho_texto": 0,
                "erro": "pytesseract não instalado",
            }
        except Exception as e:
            return {
                "tem_texto": False,
                "texto": "",
                "confianca": 0,
                "tamanho_texto": 0,
                "erro": str(e),
            }

    def processar(self) -> dict:
        """
        Processa todas as imagens na pasta de origem.

        Returns:
            dict: Estatísticas do processamento.
        """
        import shutil

        if not self._verificar_tesseract():
            print("❌ ERRO: Tesseract OCR não está disponível.")
            print("   Instale: pip install pytesseract")
            print("   E instale Tesseract OCR no sistema:")
            print("   - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   - Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por")
            print("   - macOS: brew install tesseract tesseract-lang")
            return {"com_texto": 0, "sem_texto": 0}

        pasta_origem = Path(self.pasta_origem).resolve()
        pasta_com_texto = Path(self.pasta_com_texto).resolve()
        pasta_sem_texto = Path(self.pasta_sem_texto).resolve()

        pasta_com_texto.mkdir(parents=True, exist_ok=True)
        pasta_sem_texto.mkdir(parents=True, exist_ok=True)

        if not pasta_origem.exists():
            print(f"❌ Erro: Pasta não encontrada: {pasta_origem}")
            return {"com_texto": 0, "sem_texto": 0}

        arquivos = [
            f
            for f in pasta_origem.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print(f"ℹ️  Nenhuma imagem encontrada em {pasta_origem}")
            return {"com_texto": 0, "sem_texto": 0}

        print(f"🚀 Analisando {len(arquivos)} imagem(ns) com OCR...")
        print("-" * 60)

        com_texto = 0
        sem_texto = 0

        with ProgressBar(
            total=len(arquivos), desc="Analisando OCR", unit="img"
        ).context() as pbar:
            for arquivo in arquivos:
                resultado = self._analisar_imagem(arquivo)

                if resultado.get("erro"):
                    print(f"\n⚠️  {arquivo.name}: {resultado['erro']}")
                    sem_texto += 1
                elif resultado["tem_texto"]:
                    dest = pasta_com_texto / arquivo.name
                    com_texto += 1
                    print(
                        f"\n✅ {arquivo.name}: Texto detectado ({resultado['tamanho_texto']} chars, confiança: {resultado['confianca']:.1f}%)"
                    )
                else:
                    dest = pasta_sem_texto / arquivo.name
                    sem_texto += 1

                # Move arquivo
                if "dest" in locals():
                    if dest.exists():
                        dest.unlink()
                    shutil.move(str(arquivo), str(dest))

                pbar.update(1)

        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("-" * 60)
        print(f"✅ Com texto: {com_texto}")
        print(f"❌ Sem texto: {sem_texto}")
        print(f"📁 Com texto: {pasta_com_texto}")
        print(f"📁 Sem texto: {pasta_sem_texto}")
        print("-" * 60)

        return {"com_texto": com_texto, "sem_texto": sem_texto}
