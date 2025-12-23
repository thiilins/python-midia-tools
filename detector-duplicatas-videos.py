#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de Duplicatas de Vídeos
=================================
Encontra vídeos duplicados usando hash MD5 (amostra).
"""

import sys
import os
from media_tools.video.duplicate_detector import DetectorDuplicatasVideos


def main():
    """Função principal."""
    # Verifica se deve remover automaticamente
    remover = os.getenv("REMOVER_DUPLICATAS", "false").lower() == "true"

    if len(sys.argv) > 1 and sys.argv[1] in ["--remover", "-r"]:
        remover = True

    try:
        detector = DetectorDuplicatasVideos(remover_automaticamente=remover)
        detector.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


