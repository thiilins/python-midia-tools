#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compressor de Vídeos com Máxima Compressão
===========================================
Script para comprimir vídeos usando FFmpeg com codec H.265/HEVC.
Ideal para vídeos longos (ex: 4 horas) que precisam reduzir muito o tamanho.
Inclui barra de progresso em tempo real e opções de redução de resolução.
Usa H.265 (HEVC) que comprime 40-50% melhor que H.264.
"""

import sys
import os
from media_tools.video.compressor import CompressorVideo


def main():
    """Função principal."""
    # Verifica se deve listar presets
    if len(sys.argv) > 1 and sys.argv[1] in ["--presets", "-p", "--list"]:
        print("\n📋 Presets de Compressão Disponíveis (H.265/HEVC):")
        print("=" * 70)
        presets = CompressorVideo.listar_presets()
        for nome, config in presets.items():
            marcador = " (padrão)" if nome == "master_720p" else ""
            print(f"\n{nome}{marcador}:")
            print(f"  Descrição: {config['descricao']}")
            print(f"  CRF: {config['crf']} | Preset: {config['preset']}")
            if config.get('max_resolution'):
                print(f"  Resolução Máxima: {config['max_resolution']}")
            if config.get('max_bitrate'):
                print(f"  Bitrate Máximo: {config['max_bitrate']}")
        print("\n" + "=" * 70)
        print("\n🎯 Uso:")
        print("  python otimizador-compressor-video.py                        # Usa preset padrão")
        print("  python otimizador-compressor-video.py --preset maximum_compression")
        print("  python otimizador-compressor-video.py --preset ultra_compression_1080p")
        print("\n💡 Presets recomendados por caso de uso:")
        print("   - stream_720p:            Streams e gravações longas (15GB+) → 720p boa qualidade")
        print("   - stream_480p:            Streams longas, arquivo mínimo → 480p")
        print("   - ultra_compression_720p: Compressão máxima 720p (mais agressivo)")
        print("   - maximum_compression:    Mantém resolução original, compressão máxima")
        print("   - ultra_compression_1080p: Reduz para 1080p + compressão máxima")
        print("\nOu via variável de ambiente:")
        print("  set PRESET_VIDEO=stream_720p")
        print("  python otimizador-compressor-video.py")
        print("\n🔧 Flags de execução:")
        print("  --amd                     # GPU AMD (hevc_amf + decode d3d11va) — RX 9060 XT")
        print("  --nvidia                  # GPU NVIDIA (hevc_nvenc)")
        print("  --gpu / -g                # GPU auto-detect (testa nvenc → qsv → amf)")
        print("  --sem-correcoes           # Pula correção de VFR/timestamps (mais rápido)")
        print("  --delete / -d             # Apaga originais após conversão bem-sucedida")
        print("\n⚙️  Controle de Recursos (variáveis de ambiente):")
        print("  FFMPEG_CPU_CORES=8        # Cores físicos para o encoder x265 (padrão: total-2)")
        print("  FFMPEG_THREADS=12         # Threads I/O do FFmpeg (padrão: 50% dos lógicos)")
        print("  LIMITE_CPU=85             # Limite de uso de CPU em % (padrão: 85%)")
        print("  LIMITE_MEMORIA=85         # Limite de uso de memória em % (padrão: 85%)")
        print("  ENCODER_VELOCIDADE=rapido # faster/normal/lento (sobrescreve preset do encoder)")
        print("  USAR_GPU=1                # Equivalente ao --gpu (env var)")
        print("\n💡 Com GPU AMD RX 9060 XT:")
        print("  python otimizador-compressor-video.py --amd                               # hevc_amf 5-10x mais rápido")
        print("  python otimizador-compressor-video.py --amd --preset stream_720p")
        print("  set GPU_ENCODER=amf && python otimizador-compressor-video.py  # via env")
        print("\n⚠️  IMPORTANTE: H.265 é ~50% mais lento que H.264, mas comprime muito mais!")
        sys.exit(0)

    # Padrão: GPU AMD (hevc_amf + d3d11va)
    if not os.getenv("USAR_GPU"):
        os.environ["USAR_GPU"] = "1"
        os.environ.setdefault("GPU_ENCODER", "hevc_amf")

    # Verifica preset via variável de ambiente ou argumento
    preset_nome = os.getenv("PRESET_VIDEO", None)

    # Verifica se deve corrigir problemas (padrão: True)
    corrigir_problemas = True
    env_corrigir = os.getenv("CORRIGIR_PROBLEMAS", "").lower()
    if env_corrigir in ["false", "0", "no", "off"]:
        corrigir_problemas = False

    # Processa argumentos
    deletar_originais = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ["--preset", "-P"] and i + 1 < len(args):
            preset_nome = args[i + 1]
            i += 2
        elif args[i] in ["--sem-correcoes", "--no-fix", "--no-correcoes"]:
            corrigir_problemas = False
            i += 1
        elif args[i] in ["--delete", "--apagar", "-d"]:
            deletar_originais = True
            i += 1
        elif args[i] in ["--gpu", "-g"]:
            os.environ["USAR_GPU"] = "1"
            i += 1
        elif args[i] in ["--amd"]:
            os.environ["USAR_GPU"] = "1"
            os.environ["GPU_ENCODER"] = "hevc_amf"
            i += 1
        elif args[i] in ["--nvidia"]:
            os.environ["USAR_GPU"] = "1"
            os.environ["GPU_ENCODER"] = "hevc_nvenc"
            i += 1
        elif args[i] in ["--gpu-device"] and i + 1 < len(args):
            os.environ["GPU_DEVICE"] = args[i + 1]
            i += 2
        else:
            i += 1

    try:
        if preset_nome:
            compressor = CompressorVideo(
                preset_nome=preset_nome, corrigir_problemas=corrigir_problemas
            )
        else:
            compressor = CompressorVideo(
                preset_nome="master_720p", corrigir_problemas=corrigir_problemas
            )

        compressor.processar(deletar_originais=deletar_originais)
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
