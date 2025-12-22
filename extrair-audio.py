#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Áudio
=================
Extrai áudio de vídeos (MP3, AAC, OGG, WAV).
"""

import sys
from media_tools.video.extractor import ExtratorAudio
from media_tools.common.validators import verificar_ffmpeg


def main():
    """Função principal."""
    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        # Formato padrão: MP3, qualidade: 192k
        extrator = ExtratorAudio(formato="mp3", qualidade="192k")
        extrator.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

