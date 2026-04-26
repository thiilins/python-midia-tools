#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unificador de Vídeo
===================
Lê merge-settings.json e concatena grupos de vídeos em ordem (copy mode).
"""

import argparse
import sys
from media_tools.video.merger2 import UnificadorVideo
from media_tools.common.validators import verificar_ffmpeg


def main():
    parser = argparse.ArgumentParser(description="Unifica vídeos em ordem via merge-settings.json.", add_help=False)
    parser.add_argument("--delete", action="store_true", help="Apaga originais após sucesso.")
    parser.add_argument("--settings", metavar="ARQUIVO", help="Settings explícito (padrão: configs/merge-settings.json).")
    parser.add_argument("--help", "-h", action="store_true")
    args = parser.parse_args()

    if args.help:
        print("\n🔗 Unificador de Vídeo — Copy Mode")
        print("=" * 50)
        print("\nLê configs/merge-settings.json e concatena grupos de vídeos em ordem.\n")
        print("Uso:")
        print("  python unir-videos.py")
        print("  python unir-videos.py --delete")
        print("  python unir-videos.py --settings outro.json\n")
        print("Formato (configs/merge-settings.json):")
        print('  [')
        print('    {')
        print('      "saida": "resultado.mp4",')
        print('      "videos": ["parte1.mp4", "parte2.mp4", "parte3.mp4"]')
        print('    }')
        print('  ]\n')
        print("Entrada: entrada/videos/")
        print("Saída:   saida/videos/")
        sys.exit(0)

    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        unificador = UnificadorVideo(deletar_originais=args.delete)
        unificador.processar(arquivo_settings=args.settings)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
