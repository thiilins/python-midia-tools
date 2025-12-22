#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge de Vídeos
===============
Concatena múltiplos vídeos em um único arquivo.
"""

import sys
from media_tools.video.merger import MergerVideos
from media_tools.common.validators import verificar_ffmpeg


def main():
    """Função principal."""
    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        merger = MergerVideos(nome_saida="video_merged.mp4")
        resultado = merger.processar()

        if not resultado.get("sucesso"):
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

