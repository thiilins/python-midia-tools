"""
Unificador de vídeos — lê merge-settings.json, concatena grupos de vídeos em ordem.
Copy mode — sem re-encode.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from ..common.paths import criar_pastas, obter_diretorio_base, obter_pastas_entrada_saida
from ..common.validators import verificar_ffmpeg


class UnificadorVideo:
    """
    Lê merge-settings.json de configs/ e concatena grupos de vídeos em ordem.

    Formato JSON:
    [
      {
        "saida": "resultado.mp4",
        "videos": ["parte1.mp4", "parte2.mp4", "parte3.mp4"]
      }
    ]
    """

    NOME_SETTINGS = "merge-settings.json"

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        deletar_originais: bool = False,
    ):
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = Path(pasta_entrada or entrada)
            self.pasta_saida = Path(pasta_saida or saida)
        else:
            self.pasta_entrada = Path(pasta_entrada)
            self.pasta_saida = Path(pasta_saida)

        self.deletar_originais = deletar_originais
        self.pasta_configs = obter_diretorio_base() / "configs"

    def _carregar_settings(self, arquivo_settings: Optional[Path] = None) -> list:
        if arquivo_settings:
            caminho = Path(arquivo_settings)
        else:
            caminho = self.pasta_configs / self.NOME_SETTINGS
            if not caminho.exists():
                print(f"⚠️  Settings não encontrado: {caminho}")
                return []

        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)

        return [
            {
                "saida": item["saida"],
                "videos": item["videos"],
            }
            for item in dados
        ]

    def _concatenar(self, arquivos: list, saida: Path) -> bool:
        with tempfile.TemporaryDirectory() as tmp:
            concat_list = Path(tmp) / "concat.txt"
            with open(concat_list, "w", encoding="utf-8") as f:
                for arq in arquivos:
                    f.write(f"file '{arq.as_posix()}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list),
                "-c", "copy",
                str(saida),
            ]
            resultado = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=7200)
            return resultado.returncode == 0 and saida.exists()

    def processar(self, arquivo_settings: Optional[Path] = None):
        if not verificar_ffmpeg():
            return

        criar_pastas(self.pasta_entrada, self.pasta_saida)
        grupos = self._carregar_settings(arquivo_settings)

        if not grupos:
            print("ℹ️  Nenhum grupo encontrado no settings.")
            return

        sucessos = 0
        falhas = 0

        for grupo in grupos:
            nome_saida = grupo["saida"]
            videos = grupo["videos"]

            print(f"\n🎬 {nome_saida} ← {len(videos)} arquivo(s)")

            arquivos_entrada = []
            ok = True
            for nome in videos:
                caminho = self.pasta_entrada / nome
                if not caminho.exists():
                    print(f"   ❌ Não encontrado: {caminho}")
                    ok = False
                    break
                arquivos_entrada.append(caminho)
                print(f"   + {nome}")

            if not ok:
                falhas += 1
                continue

            caminho_saida = self.pasta_saida / nome_saida
            print(f"   ⏳ Concatenando...", end="", flush=True)
            if self._concatenar(arquivos_entrada, caminho_saida):
                tamanho = caminho_saida.stat().st_size / (1024 * 1024)
                print(f" ✅ {tamanho:.1f}MB → {caminho_saida.name}")
                sucessos += 1
                if self.deletar_originais:
                    for arq in arquivos_entrada:
                        arq.unlink()
                    print(f"   🗑️  Originais removidos.")
            else:
                print(f" ❌")
                falhas += 1

        print(f"\n✅ {sucessos} grupo(s) unificado(s)" + (f" | ⚠️  {falhas} falha(s)" if falhas else ""))
