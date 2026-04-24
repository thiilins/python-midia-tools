"""
Move para a lixeira todos os vídeos com resolução ≤ 240p
em entrada/videos e saida/videos.

Uso:
  python apagar-videos-240p.py           # prévia (dry-run)
  python apagar-videos-240p.py --apagar  # move para lixeira
"""

import argparse
from pathlib import Path

import cv2
from send2trash import send2trash

EXTENSOES = {".mp4", ".m4v", ".mov", ".webm", ".mkv", ".avi"}
RESOLUCAO_MAX = 240  # lado curto ≤ 240 → 240p


def obter_resolucao(arquivo: Path):
    try:
        cap = cv2.VideoCapture(str(arquivo))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return w, h
    except Exception:
        return 0, 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apagar", action="store_true", help="Move para lixeira (sem flag = dry-run)")
    args = parser.parse_args()

    raiz = Path(__file__).parent
    pastas = [raiz / "entrada" / "videos", raiz / "saida" / "videos"]

    todos = []
    for pasta in pastas:
        if not pasta.exists():
            continue
        todos += [f for f in pasta.rglob("*") if f.suffix.lower() in EXTENSOES]

    total = len(todos)
    candidatos = []

    for i, arquivo in enumerate(todos, 1):
        print(f"\r  Verificando {i}/{total}...", end="", flush=True)
        w, h = obter_resolucao(arquivo)
        lado_curto = min(w, h) if w and h else 0
        if lado_curto and lado_curto <= RESOLUCAO_MAX:
            candidatos.append((arquivo, w, h))
            print(f"\r  🎯 {w}x{h}  {arquivo.name:<60}")

    print(f"\r{'':80}")  # limpa linha do contador

    if not candidatos:
        print("Nenhum vídeo ≤ 240p encontrado.")
        return

    print(f"\n{'[DRY-RUN] ' if not args.apagar else ''}Total: {len(candidatos)} vídeos ≤ 240p\n")

    if not args.apagar:
        print("⚠️  Dry-run — nenhum arquivo movido. Use --apagar para mover para a lixeira.")
        return

    movidos = 0
    for arquivo, w, h in candidatos:
        try:
            send2trash(str(arquivo))
            print(f"  🗑️  {arquivo.name} ({w}x{h})")
            movidos += 1
        except Exception as e:
            print(f"  ❌  {arquivo.name}: {e}")

    print(f"\n✅ {movidos}/{len(candidatos)} arquivos movidos para a lixeira.")


if __name__ == "__main__":
    main()
