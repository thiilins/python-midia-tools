"""
Clipper de vídeos — lê cut-settings.(txt|json), extrai cada segmento como clip individual.
Mesmo formato do FatiadorVideo, mas sem concatenar: cada segmento = um arquivo separado.
Saída: {stem}_clip_{uuid}.mp4
"""

import subprocess
import uuid
from pathlib import Path
from typing import Optional

from ..common.paths import criar_pastas, obter_diretorio_base, obter_pastas_entrada_saida
from ..common.validators import verificar_ffmpeg
from .cutter import _converter_tempo


class ClipperVideo:
    """
    Lê cut-settings.txt ou cut-settings.json e extrai cada segmento como um
    arquivo separado (copy mode — sem re-encode).

    Formato TXT: nome.mp4: HH:MM:SS-HH:MM:SS|HH:MM:SS-HH:MM:SS
    Formato JSON: [{"arquivo": "nome.mp4", "segmentos": ["HH:MM:SS-HH:MM:SS"]}]

    Saída: saida/clips/{stem}_clip_{uuid}.mp4
    """

    NOME_SETTINGS_TXT = "cut-settings.txt"
    NOME_SETTINGS_JSON = "cut-settings.json"

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        deletar_originais: bool = False,
    ):
        if pasta_entrada is None or pasta_saida is None:
            entrada, _ = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = Path(pasta_entrada or entrada)
        else:
            self.pasta_entrada = Path(pasta_entrada)

        if pasta_saida:
            self.pasta_saida = Path(pasta_saida)
        else:
            self.pasta_saida = obter_diretorio_base() / "saida" / "clips"

        self.deletar_originais = deletar_originais
        self.pasta_configs = obter_diretorio_base() / "configs"

    def _carregar_settings(self, arquivo_settings: Optional[Path] = None) -> list:
        if arquivo_settings:
            caminho = Path(arquivo_settings)
        else:
            json_path = self.pasta_configs / self.NOME_SETTINGS_JSON
            txt_path = self.pasta_configs / self.NOME_SETTINGS_TXT
            if json_path.exists():
                caminho = json_path
            elif txt_path.exists():
                caminho = txt_path
            else:
                print(f"⚠️  Nenhum settings encontrado em {self.pasta_configs}")
                return []

        if caminho.suffix == ".json":
            return self._carregar_json(caminho)
        return self._carregar_txt(caminho)

    def _carregar_json(self, caminho: Path) -> list:
        import json
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        return [{"arquivo": item["arquivo"], "segmentos": item["segmentos"]} for item in dados]

    def _carregar_txt(self, caminho: Path) -> list:
        entradas = []
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                partes = linha.split(":", 1)
                if len(partes) != 2:
                    continue
                arquivo = partes[0].strip()
                segmentos = [s.strip() for s in partes[1].split("|") if s.strip()]
                if arquivo and segmentos:
                    entradas.append({"arquivo": arquivo, "segmentos": segmentos})
        return entradas

    def _parsear_segmento(self, segmento: str):
        partes = segmento.split("-", 1)
        if len(partes) != 2:
            raise ValueError(f"Segmento inválido: '{segmento}'. Use 'HH:MM:SS-HH:MM:SS'.")
        return _converter_tempo(partes[0]), _converter_tempo(partes[1])

    def _extrair_clip(self, entrada: Path, saida: Path, inicio: float, fim: float) -> bool:
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-i", str(entrada),
            "-t", str(fim - inicio),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            str(saida),
        ]
        resultado = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3600)
        return resultado.returncode == 0 and saida.exists()

    def processar(self, arquivo_settings: Optional[Path] = None):
        if not verificar_ffmpeg():
            return

        criar_pastas(self.pasta_entrada, self.pasta_saida)
        entradas = self._carregar_settings(arquivo_settings)

        if not entradas:
            print("ℹ️  Nenhuma entrada encontrada no settings.")
            return

        total_clips = 0
        falhas = 0

        for entrada in entradas:
            nome_arquivo = entrada["arquivo"]
            segmentos = entrada["segmentos"]
            arquivo_origem = self.pasta_entrada / nome_arquivo

            if not arquivo_origem.exists():
                print(f"⚠️  Arquivo não encontrado: {arquivo_origem}")
                falhas += 1
                continue

            print(f"\n📹 {nome_arquivo} — {len(segmentos)} segmento(s)")

            clips_ok = []
            for segmento in segmentos:
                try:
                    inicio, fim = self._parsear_segmento(segmento)
                except ValueError as e:
                    print(f"   ❌ {e}")
                    falhas += 1
                    continue

                clip_id = str(uuid.uuid4())[:8]
                nome_saida = f"{arquivo_origem.stem}_clip_{clip_id}.mp4"
                caminho_saida = self.pasta_saida / nome_saida

                print(f"   ✂️  {segmento} → {nome_saida}", end="", flush=True)
                ok = self._extrair_clip(arquivo_origem, caminho_saida, inicio, fim)

                if ok:
                    tamanho = caminho_saida.stat().st_size / (1024 * 1024)
                    print(f" ({tamanho:.1f}MB) ✅")
                    clips_ok.append(caminho_saida)
                    total_clips += 1
                else:
                    print(" ❌")
                    falhas += 1

            if clips_ok and self.deletar_originais:
                arquivo_origem.unlink()
                print(f"   🗑️  Original removido.")

        print(f"\n✅ {total_clips} clip(s) gerado(s) em {self.pasta_saida}")
        if falhas:
            print(f"⚠️  {falhas} falha(s)")
