#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corretor de Vídeos - Correção de Framerate e Problemas Gerais
==============================================================
Script para corrigir problemas em vídeos MP4/M4V/MOV usando FFmpeg.
Inclui correção de:
- VFR (Variable Frame Rate) - converte para framerate constante
- Problemas com timestamps
- Dessincronia de áudio

Inclui barra de progresso em tempo real usando tqdm e ffprobe.
"""

import sys
import os
from media_tools.video.corrector import CorretorVideo


def main():
    """Função principal."""
    # Verifica se deve mostrar ajuda
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "--ajuda"]:
        print("\n🔧 Corretor de Vídeos - Correção de Framerate e Problemas Gerais")
        print("=" * 70)
        print("\nEste script corrige problemas comuns em vídeos:")
        print("  • VFR (Variable Frame Rate) - converte para framerate constante")
        print("  • Problemas com timestamps")
        print("  • Dessincronia de áudio")
        print("\nUso:")
        print("  python corretor-video.py                    # Corrige todos os problemas")
        print("  python corretor-video.py --sem-vfr          # Não corrige VFR")
        print("  python corretor-video.py --sem-timestamps   # Não corrige timestamps")
        print("  python corretor-video.py --sem-audio        # Não corrige áudio")
        print("\nOu via variável de ambiente:")
        print("  export CORRIGIR_VFR=false          # Desabilita correção de VFR")
        print("  export CORRIGIR_TIMESTAMPS=false   # Desabilita correção de timestamps")
        print("  export CORRIGIR_AUDIO=false         # Desabilita correção de áudio")
        print("  python corretor-video.py")
        print("\n🔧 Controle de Recursos (variáveis de ambiente):")
        print(
            "  FFMPEG_THREADS=4          # Número de threads (padrão: 50% dos cores, máx 8)"
        )
        print("  LIMITE_CPU=85              # Limite de uso de CPU em % (padrão: 85%)")
        print(
            "  LIMITE_MEMORIA=85         # Limite de uso de memória em % (padrão: 85%)"
        )
        print(
            "  PAUSA_ENTRE_VIDEOS=1.0    # Pausa entre vídeos em segundos (padrão: 1.0s)"
        )
        print("\n⚠️  IMPORTANTE: O corretor controla automaticamente o uso de")
        print("   recursos para evitar sobrecarga do sistema.")
        sys.exit(0)

    # Verifica configurações via variáveis de ambiente ou argumentos
    corrigir_vfr = os.getenv("CORRIGIR_VFR", "true").lower() not in ["false", "0", "no", "off"]
    corrigir_timestamps = os.getenv("CORRIGIR_TIMESTAMPS", "true").lower() not in ["false", "0", "no", "off"]
    corrigir_audio = os.getenv("CORRIGIR_AUDIO", "true").lower() not in ["false", "0", "no", "off"]

    # Processa argumentos
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ["--sem-vfr", "--no-vfr", "--sem-framerate"]:
                corrigir_vfr = False
            elif arg in ["--sem-timestamps", "--no-timestamps"]:
                corrigir_timestamps = False
            elif arg in ["--sem-audio", "--no-audio"]:
                corrigir_audio = False

    try:
        corretor = CorretorVideo(
            corrigir_vfr=corrigir_vfr,
            corrigir_timestamps=corrigir_timestamps,
            corrigir_audio=corrigir_audio,
        )

        corretor.processar(deletar_originais=False)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

