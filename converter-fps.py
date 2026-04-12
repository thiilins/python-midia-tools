#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor de FPS
================
Reduz framerate de vídeos (ex: 60fps → 30fps).
60fps → 30fps reduz ~30-40% do tamanho antes de qualquer compressão.
"""

import sys
import os
from media_tools.video.fps_converter import ConversorFPS
from media_tools.common.validators import verificar_ffmpeg


def main():
    """Função principal."""
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "--ajuda"):
        print("\n🎞️  Conversor de FPS")
        print("=" * 55)
        print("\nReduz framerate de vídeos (ex: 60fps → 30fps).")
        print("60fps → 30fps reduz ~30-40% antes de qualquer compressão.")
        print("\nUso:")
        print("  python converter-fps.py                # converte para 30fps (padrão)")
        print("  python converter-fps.py --fps 24       # converte para 24fps")
        print("  python converter-fps.py --fps 60       # converte para 60fps")
        print("\nPré-processamento recomendado para streams:")
        print("  python converter-fps.py --fps 30       # 1. reduz FPS (30-40% menor)")
        print("  python otimizador-compressor-video.py  # 2. H.265 (mais 60-70% menor)")
        print("\nVariáveis de ambiente:")
        print("  FFMPEG_THREADS=12   # Threads I/O (padrão: 50% dos lógicos)")
        print("\nArquivos com FPS já <= alvo são pulados automaticamente.")
        print("Saída em saida/videos/ com sufixo _{fps}fps.mp4")
        sys.exit(0)

    if not verificar_ffmpeg():
        sys.exit(1)

    # Parse --fps N
    fps_alvo = 30
    if "--fps" in sys.argv:
        idx = sys.argv.index("--fps")
        if idx + 1 < len(sys.argv):
            try:
                fps_alvo = int(sys.argv[idx + 1])
                if fps_alvo < 1 or fps_alvo > 120:
                    print("❌ FPS deve ser entre 1 e 120.")
                    sys.exit(1)
            except ValueError:
                print("❌ Valor de FPS inválido.")
                sys.exit(1)

    # deletar_originais via env
    deletar = os.getenv("DELETAR_ORIGINAIS", "false").lower() in ("true", "1", "yes")

    try:
        conversor = ConversorFPS(fps_alvo=fps_alvo, deletar_originais=deletar)
        conversor.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
