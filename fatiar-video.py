#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fatiador de Vídeo
=================
Lê cut-settings.txt ou cut-settings.json, extrai os segmentos especificados
e os concatena num único arquivo por vídeo (copy mode — sem re-encode).
"""

import argparse
import sys
from media_tools.video.slicer import FatiadorVideo
from media_tools.common.validators import verificar_ffmpeg


def main():
    parser = argparse.ArgumentParser(
        description="Fatia e concatena segmentos de vídeo a partir de cut-settings.(txt|json).",
        add_help=False,
    )
    parser.add_argument("--delete", action="store_true", help="Apaga originais após processamento bem-sucedido.")
    parser.add_argument("--settings", metavar="ARQUIVO", help="Arquivo de settings explícito (padrão: auto-detecta).")
    parser.add_argument("--help", "-h", action="store_true")
    args = parser.parse_args()

    if args.help:
        print("\n✂️  Fatiador de Vídeo — Copy Mode")
        print("=" * 50)
        print("\nLê cut-settings.txt ou cut-settings.json e extrai os segmentos")
        print("especificados, concatenando-os num único arquivo por vídeo.")
        print("Copy mode: sem re-encode, instantâneo.\n")
        print("Uso:")
        print("  python fatiar-video.py")
        print("  python fatiar-video.py --delete")
        print("  python fatiar-video.py --settings meu-arquivo.json\n")
        print("Formato TXT (entrada/videos/cut-settings.txt):")
        print("  video.mp4: 00:00:00-00:10:00|00:12:00-00:20:00")
        print("  outro.mp4: 00:05:00-00:30:00\n")
        print("Formato JSON (entrada/videos/cut-settings.json):")
        print('  [')
        print('    {')
        print('      "arquivo": "video.mp4",')
        print('      "segmentos": ["00:00:00-00:10:00", "00:12:00-00:20:00"]')
        print('    }')
        print('  ]\n')
        print("Settings em: entrada/videos/")
        print("Saída em:    saida/videos/")
        sys.exit(0)

    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        fatiador = FatiadorVideo(deletar_originais=args.delete)
        fatiador.processar(arquivo_settings=args.settings)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
