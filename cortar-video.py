#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cortador de Vídeo
=================
Extrai segmentos de vídeos por timestamp usando copy mode.
Copy mode = sem re-encode, instantâneo mesmo em arquivos de 15GB.
"""

import sys
from media_tools.video.cutter import CortadorVideo
from media_tools.common.validators import verificar_ffmpeg


def main():
    """Função principal."""
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "--ajuda"):
        print("\n✂️  Cortador de Vídeo — Copy Mode")
        print("=" * 50)
        print("\nExtrai segmentos de vídeo por timestamp.")
        print("Copy mode: sem re-encode, instantâneo mesmo em arquivos de 15GB.")
        print("\nUso:")
        print("  python cortar-video.py")
        print("\nO script exibe os vídeos disponíveis em entrada/videos/")
        print("e solicita início, fim e nome do clip interativamente.")
        print("\nFormatos de tempo aceitos:")
        print("  00:10:30  →  HH:MM:SS")
        print("  10:30     →  MM:SS")
        print("  630       →  segundos")
        print("\nClips salvos em: saida/clips/")
        sys.exit(0)

    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        cortador = CortadorVideo()
        cortador.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
