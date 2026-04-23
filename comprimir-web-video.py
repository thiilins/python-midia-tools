"""
Compressor de vídeos para streaming web.
Converte para H.264 + faststart — permite seek no player antes do download completo.
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Comprime vídeos para streaming web (H.264 + faststart)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--crf", type=str, default="22",
        help="Qualidade (0-51, menor = melhor). Padrão: 22",
    )
    parser.add_argument(
        "--preset", type=str, default="medium",
        choices=["ultrafast", "superfast", "veryfast", "faster", "fast",
                 "medium", "slow", "slower", "veryslow"],
        help="Velocidade de encoding vs compressão. Padrão: medium",
    )
    parser.add_argument(
        "--audio-bitrate", type=str, default="192k",
        help="Bitrate do áudio AAC. Padrão: 192k",
    )
    parser.add_argument(
        "--gpu-device", type=int, default=None,
        help="Índice do adaptador GPU (padrão: 0 via GPU_DEVICE env)",
    )
    parser.add_argument(
        "--no-gpu", action="store_true",
        help="Forçar uso de CPU (libx264) mesmo com GPU disponível",
    )
    parser.add_argument(
        "--keep", "-k", action="store_true",
        help="Manter os arquivos originais após a conversão",
    )

    args = parser.parse_args()

    # Aplica flags de GPU antes de importar o módulo
    if args.no_gpu:
        os.environ["USAR_GPU"] = "0"
    if args.gpu_device is not None:
        os.environ["GPU_DEVICE"] = str(args.gpu_device)

    from media_tools.video.web_compressor import CompressorWebVideo

    compressor = CompressorWebVideo(
        crf=args.crf,
        preset=args.preset,
        audio_bitrate=args.audio_bitrate,
    )

    resultado = compressor.processar(deletar_originais=not args.keep)

    if resultado["falhas"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
