#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador de Vídeos com Barra de Progresso
===========================================
Script para otimizar vídeos MP4/M4V usando FFmpeg com codec H.264.
Inclui barra de progresso em tempo real usando tqdm e ffprobe.
Suporta presets pré-configurados para diferentes necessidades.
Corrige automaticamente problemas como VFR, timestamps e dessincronia de áudio.
"""

import sys
import os
from media_tools.video.optimizer import OtimizadorVideo


def main():
    """Função principal."""
    # Verifica se deve listar presets
    if len(sys.argv) > 1 and sys.argv[1] in ["--presets", "-p", "--list"]:
        print("\n📋 Presets Disponíveis:")
        print("=" * 60)
        presets = OtimizadorVideo.listar_presets()
        for nome, config in presets.items():
            marcador = " (padrão)" if nome == "medium" else ""
            print(f"\n{nome}{marcador}:")
            print(f"  Descrição: {config['descricao']}")
            print(f"  CRF: {config['crf']} | Preset: {config['preset']}")
        print("\n" + "=" * 60)
        print("\nUso:")
        print("  python otimizador-video.py                    # Usa preset 'medium' (padrão)")
        print("  python otimizador-video.py --preset ultra_fast # Usa preset ultra_fast")
        print("  python otimizador-video.py --preset maximum   # Usa preset maximum")
        print("  python otimizador-video.py --sem-correcoes    # Desabilita correções automáticas")
        print("\nOu via variável de ambiente:")
        print("  export PRESET_VIDEO=high_quality")
        print("  export CORRIGIR_PROBLEMAS=false  # Desabilita correções")
        print("  python otimizador-video.py")
        print("\n💡 Por padrão, o otimizador detecta e corrige:")
        print("   - VFR (Variable Frame Rate)")
        print("   - Problemas com timestamps")
        print("   - Dessincronia de áudio")
        sys.exit(0)

    # Verifica preset via variável de ambiente ou argumento
    preset_nome = os.getenv("PRESET_VIDEO", None)

    # Verifica se deve corrigir problemas (padrão: True)
    corrigir_problemas = True
    env_corrigir = os.getenv("CORRIGIR_PROBLEMAS", "").lower()
    if env_corrigir in ["false", "0", "no", "off"]:
        corrigir_problemas = False

    # Processa argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--preset", "-P"] and len(sys.argv) > 2:
            preset_nome = sys.argv[2]
        elif sys.argv[1] in ["--sem-correcoes", "--no-fix", "--no-correcoes"]:
            corrigir_problemas = False

    try:
        # Se preset_nome foi fornecido, usa preset; senão usa padrão (medium)
        if preset_nome:
            otimizador = OtimizadorVideo(
                preset_nome=preset_nome,
                corrigir_problemas=corrigir_problemas
            )
        else:
            # Padrão: medium
            otimizador = OtimizadorVideo(
                preset_nome="medium",
                corrigir_problemas=corrigir_problemas
            )

        otimizador.processar(deletar_originais=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
