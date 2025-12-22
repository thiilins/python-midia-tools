#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador de Vídeos com Barra de Progresso
===========================================
Script para otimizar vídeos MP4/M4V usando FFmpeg com codec H.264.
Inclui barra de progresso em tempo real usando tqdm e ffprobe.
"""

import sys
from media_tools.video.optimizer import OtimizadorVideo


def main():
    """Função principal."""
    try:
        otimizador = OtimizadorVideo(crf="23", preset="medium")
        otimizador.processar(deletar_originais=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
