#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Thumbnails
======================
Extrai thumbnails (miniaturas) de vídeos.
"""

import sys
from media_tools.video.extractor import ExtratorThumbnails
from media_tools.common.validators import verificar_ffmpeg


def main():
    """Função principal."""
    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        # Extrai 3 thumbnails por vídeo, tamanho 320x240
        extrator = ExtratorThumbnails(quantidade=3, tamanho="320x240")
        extrator.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

