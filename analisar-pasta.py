#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Pasta de Vídeos
==============================
Inventário de pasta com codec, resolução, FPS, bitrate,
duração, tamanho e estimativa de compressão H.265.
"""

import sys
from pathlib import Path
from media_tools.video.analyzer import AnalisadorMidia
from media_tools.common.validators import verificar_ffmpeg


def main():
    """Função principal."""
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "--ajuda"):
        print("\n📊 Analisador de Pasta de Vídeos")
        print("=" * 50)
        print("\nExibe inventário técnico da pasta entrada/videos/")
        print("com estimativa de tamanho pós-compressão H.265.")
        print("\nUso:")
        print("  python analisar-pasta.py              # analisa entrada/videos/")
        print("  python analisar-pasta.py /pasta/path  # analisa pasta específica")
        print("\nInformações exibidas por arquivo:")
        print("  codec, resolução, FPS, bitrate, duração, tamanho")
        print("  estimativa pós H.265 stream_720p")
        print("  recomendação de preset/workflow")
        sys.exit(0)

    if not verificar_ffmpeg():
        sys.exit(1)

    # Pasta opcional via argumento
    pasta = None
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        pasta = Path(sys.argv[1])
        if not pasta.exists():
            print(f"❌ Pasta não encontrada: {pasta}")
            sys.exit(1)

    try:
        analisador = AnalisadorMidia(pasta=pasta)
        analisador.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
