#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR de Imagens
==============
Detecta texto em imagens usando Tesseract OCR.
"""

import sys
from media_tools.image.ocr import OCRImagens


def main():
    """Função principal."""
    try:
        ocr = OCRImagens()
        ocr.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
