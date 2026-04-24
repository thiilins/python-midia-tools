"""
Move para a lixeira todos os vídeos com resolução ≤ 240p
em entrada/videos e saida/videos.

Uso:
  python apagar-videos-240p.py           # prévia (dry-run)
  python apagar-videos-240p.py --apagar  # move para lixeira
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from send2trash import send2trash

EXTENSOES = {".mp4", ".m4v", ".mov", ".webm", ".mkv", ".avi"}
RESOLUCAO_MAX = 240  # lado curto ≤ 240 → 240p


def obter_resolucao(arquivo: Path):
    try:
        resultado = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_streams", "-select_streams", "v:0", str(arquivo),
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
        )
        data = json.loads(resultado.stdout)
        stream = data.get("streams", [{}])[0]
        w = int(stream.get("width", 0))
        h = int(stream.get("height", 0))
        return w, h
    except Exception:
        return 0, 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apagar", action="store_true", help="Move para lixeira (sem flag = dry-run)")
    args = parser.parse_args()

    raiz = Path(__file__).parent
    pastas = [raiz / "entrada" / "videos", raiz / "saida" / "videos"]

    candidatos = []
    for pasta in pastas:
        if not pasta.exists():
            continue
        for arquivo in pasta.rglob("*"):
            if arquivo.suffix.lower() not in EXTENSOES:
                continue
            w, h = obter_resolucao(arquivo)
            lado_curto = min(w, h) if w and h else 0
            if lado_curto and lado_curto <= RESOLUCAO_MAX:
                candidatos.append((arquivo, w, h))

    if not candidatos:
        print("Nenhum vídeo 240p encontrado.")
        return

    print(f"\n{'[DRY-RUN] ' if not args.apagar else ''}Vídeos ≤ 240p encontrados: {len(candidatos)}\n")
    for arquivo, w, h in candidatos:
        print(f"  {w}x{h}  {arquivo}")

    if not args.apagar:
        print(f"\n⚠️  Dry-run — nenhum arquivo movido. Use --apagar para mover para a lixeira.")
        return

    print()
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
