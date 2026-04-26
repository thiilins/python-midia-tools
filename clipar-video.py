#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clipper de Vídeo
================
Lê cut-settings.txt ou cut-settings.json e extrai cada segmento como
um clip individual (copy mode — sem re-encode).

Mesmo formato do fatiar-video.py, mas sem concatenar.
Saída: saida/clips/{nome}_clip_{uuid}.mp4
"""

import argparse
import sys
from media_tools.video.clipper import ClipperVideo
from media_tools.common.validators import verificar_ffmpeg


def main():
    parser = argparse.ArgumentParser(
        description="Extrai segmentos de vídeo como clips individuais via cut-settings.",
        add_help=False,
    )
    parser.add_argument("--delete", action="store_true", help="Apaga originais após processamento bem-sucedido.")
    parser.add_argument("--settings", metavar="ARQUIVO", help="Arquivo de settings explícito (padrão: auto-detecta).")
    parser.add_argument("--help", "-h", action="store_true")
    args = parser.parse_args()

    if args.help:
        print("\n✂️  Clipper de Vídeo — Copy Mode")
        print("=" * 50)
        print("\nLê cut-settings.txt ou cut-settings.json e extrai cada segmento")
        print("como um arquivo separado (sem concatenar, sem re-encode).\n")
        print("Uso:")
        print("  python clipar-video.py")
        print("  python clipar-video.py --delete")
        print("  python clipar-video.py --settings meu-arquivo.json\n")
        print("Formato JSON (configs/cut-settings.json):")
        print('  [')
        print('    {')
        print('      "arquivo": "video.mp4",')
        print('      "segmentos": ["00:00:00-00:10:00", "00:12:00-00:20:00"]')
        print('    }')
        print('  ]\n')
        print("Formato TXT (configs/cut-settings.txt):")
        print("  video.mp4: 00:00:00-00:10:00|00:12:00-00:20:00\n")
        print("Settings em: configs/")
        print("Entrada em:  entrada/videos/")
        print("Saída em:    saida/clips/{nome}_clip_{uuid}.mp4")
        sys.exit(0)

    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        clipper = ClipperVideo(deletar_originais=args.delete)
        clipper.processar(arquivo_settings=args.settings)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
