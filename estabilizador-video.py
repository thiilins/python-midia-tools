#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estabilizador de Vídeo
======================
Estabiliza vídeos tremidos e corrige rotação automática.
"""

import sys
from media_tools.video.stabilizer import EstabilizadorVideo
from media_tools.common.validators import verificar_ffmpeg


def main():
    """Função principal."""
    if not verificar_ffmpeg():
        sys.exit(1)

    try:
        estabilizador = EstabilizadorVideo(correcao_rotacao=True)
        estabilizador.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
