#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Thumbnails
=====================
Gera thumbnails de imagens e vídeos em múltiplos tamanhos.
"""

import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image

from media_tools.common.paths import obter_diretorio_base, obter_pastas_entrada_saida
from media_tools.common.progress import ProgressBar
from media_tools.common.validators import verificar_ffmpeg


def gerar_thumbnail_imagem(arquivo: Path, pasta_saida: Path, tamanhos: list) -> int:
    """
    Gera thumbnails de uma imagem.

    Args:
        arquivo: Caminho da imagem.
        pasta_saida: Pasta de saída.
        tamanhos: Lista de tamanhos (ex: ["320x240", "640x480"]).

    Returns:
        int: Número de thumbnails geradas.
    """
    sucessos = 0
    try:
        img = Image.open(arquivo)
        img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)  # Reduz se muito grande

        for tamanho in tamanhos:
            try:
                largura, altura = map(int, tamanho.split("x"))
                img_thumb = img.copy()
                img_thumb.thumbnail((largura, altura), Image.Resampling.LANCZOS)

                nome_thumb = f"{arquivo.stem}_{tamanho}.jpg"
                caminho_thumb = pasta_saida / nome_thumb
                img_thumb.save(caminho_thumb, "JPEG", quality=85, optimize=True)
                sucessos += 1
            except Exception:
                pass
    except Exception:
        pass

    return sucessos


def gerar_thumbnail_video(arquivo: Path, pasta_saida: Path, tamanhos: list) -> int:
    """
    Gera thumbnails de um vídeo.

    Args:
        arquivo: Caminho do vídeo.
        pasta_saida: Pasta de saída.
        tamanhos: Lista de tamanhos.

    Returns:
        int: Número de thumbnails geradas.
    """
    if not verificar_ffmpeg():
        return 0

    sucessos = 0
    duracao = 0

    # Obtém duração
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(arquivo),
        ]
        resultado = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        if resultado.returncode == 0:
            duracao = float(resultado.stdout.strip())
    except Exception:
        duracao = 10  # Fallback

    tempo_frame = duracao / 2  # Frame do meio

    for tamanho in tamanhos:
        try:
            largura, altura = tamanho.split("x")
            nome_thumb = f"{arquivo.stem}_{tamanho}.jpg"
            caminho_thumb = pasta_saida / nome_thumb

            cmd = [
                "ffmpeg",
                "-y",
                "-ss",
                str(tempo_frame),
                "-i",
                str(arquivo),
                "-vframes",
                "1",
                "-vf",
                f"scale={largura}:{altura}",
                str(caminho_thumb),
            ]

            resultado = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30
            )

            if resultado.returncode == 0 and caminho_thumb.exists():
                sucessos += 1
        except Exception:
            pass

    return sucessos


def main():
    """Função principal."""
    base = obter_diretorio_base()
    pasta_imagens = base / "entrada" / "imagens"
    pasta_videos = base / "entrada" / "videos"
    pasta_saida = base / "saida" / "thumbnails"

    pasta_saida.mkdir(parents=True, exist_ok=True)

    # Tamanhos padrão
    tamanhos = ["320x240", "640x480", "1280x720"]

    print("🚀 Gerando thumbnails...")
    print(f"⚙️  Tamanhos: {', '.join(tamanhos)}")
    print("-" * 60)

    total_gerados = 0

    # Processa imagens
    if pasta_imagens.exists():
        imagens = [
            f
            for f in pasta_imagens.iterdir()
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ]

        if imagens:
            print(f"\n📸 Processando {len(imagens)} imagem(ns)...")
            with ProgressBar(total=len(imagens), desc="Imagens", unit="img").context() as pbar:
                for img in imagens:
                    gerados = gerar_thumbnail_imagem(img, pasta_saida, tamanhos)
                    total_gerados += gerados
                    pbar.update(1)

    # Processa vídeos
    if pasta_videos.exists() and verificar_ffmpeg():
        videos = [
            f
            for f in pasta_videos.iterdir()
            if f.is_file() and f.suffix.lower() in {".mp4", ".m4v", ".mov", ".webm", ".avi"}
        ]

        if videos:
            print(f"\n🎬 Processando {len(videos)} vídeo(s)...")
            with ProgressBar(total=len(videos), desc="Vídeos", unit="vídeo").context() as pbar:
                for video in videos:
                    gerados = gerar_thumbnail_video(video, pasta_saida, tamanhos)
                    total_gerados += gerados
                    pbar.update(1)

    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("-" * 60)
    print(f"🖼️  Total de thumbnails geradas: {total_gerados}")
    print(f"📁 Arquivos salvos em: {pasta_saida}")
    print("-" * 60)

    if total_gerados == 0:
        print("ℹ️  Nenhum arquivo encontrado para processar.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

