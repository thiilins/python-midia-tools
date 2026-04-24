"""
Fatiador de vídeos — lê cut-settings.(txt|json), extrai segmentos e concatena em copy mode.
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from ..common.paths import criar_pastas, obter_diretorio_base, obter_pastas_entrada_saida
from ..common.validators import verificar_ffmpeg
from .cutter import _converter_tempo, _formatar_tempo


class FatiadorVideo:
    """
    Lê cut-settings.txt ou cut-settings.json, extrai os segmentos especificados
    e concatena num único arquivo por vídeo (copy mode — sem re-encode).

    Formato TXT: nome.mp4: HH:MM:SS-HH:MM:SS|HH:MM:SS-HH:MM:SS
    Formato JSON: [{"arquivo": "nome.mp4", "segmentos": ["HH:MM:SS-HH:MM:SS"]}]
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
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = Path(pasta_entrada or entrada)
            self.pasta_saida = Path(pasta_saida or saida)
        else:
            self.pasta_entrada = Path(pasta_entrada)
            self.pasta_saida = Path(pasta_saida)
        self.deletar_originais = deletar_originais
        self.pasta_configs = obter_diretorio_base() / "configs"

    def _carregar_settings(self, arquivo_settings: Optional[Path] = None) -> list:
        """
        Carrega cut-settings.json ou cut-settings.txt de configs/ na raiz do projeto.
        JSON tem prioridade quando ambos existem.
        Retorna lista de dicts: [{"arquivo": str, "segmentos": ["HH:MM:SS-HH:MM:SS", ...]}]
        """
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
        """Parseia 'HH:MM:SS-HH:MM:SS' para (inicio_float, fim_float)."""
        partes = segmento.split("-", 1)
        if len(partes) != 2:
            raise ValueError(f"Segmento inválido: '{segmento}'. Use 'HH:MM:SS-HH:MM:SS'.")
        return _converter_tempo(partes[0]), _converter_tempo(partes[1])

    def _extrair_segmento(self, entrada: Path, saida: Path, inicio: float, fim: float) -> bool:
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

    def _concatenar(self, segmentos_temp: list, saida: Path) -> bool:
        """Concatena via concat demuxer. Com um único segmento, apenas move o arquivo."""
        if len(segmentos_temp) == 1:
            shutil.move(str(segmentos_temp[0]), str(saida))
            return saida.exists()

        concat_list = saida.parent / f"_concat_{saida.stem}.txt"
        try:
            with open(concat_list, "w", encoding="utf-8") as f:
                for seg in segmentos_temp:
                    f.write(f"file '{seg.as_posix()}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list),
                "-c", "copy",
                str(saida),
            ]
            resultado = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3600)
            return resultado.returncode == 0 and saida.exists()
        finally:
            if concat_list.exists():
                concat_list.unlink()

    def processar(self, arquivo_settings: Optional[Path] = None) -> dict:
        if not verificar_ffmpeg():
            return {"processados": 0, "falhas": 0}

        criar_pastas(self.pasta_entrada, self.pasta_saida)

        entradas = self._carregar_settings(arquivo_settings)
        if not entradas:
            print(f"ℹ️  Nenhum settings encontrado em {self.pasta_entrada}")
            print(f"   Crie '{self.NOME_SETTINGS_TXT}' ou '{self.NOME_SETTINGS_JSON}'")
            return {"processados": 0, "falhas": 0}

        print("\n" + "=" * 60)
        print("✂️   FATIADOR DE VÍDEO — COPY MODE")
        print("=" * 60)
        print(f"Entradas: {len(entradas)} vídeo(s)\n")

        processados = 0
        falhas = 0

        for entrada in entradas:
            nome_arquivo = entrada["arquivo"]
            segmentos_str = entrada["segmentos"]
            arquivo_origem = self.pasta_entrada / nome_arquivo

            print(f"📹 {nome_arquivo}")

            if not arquivo_origem.exists():
                print(f"   ❌ Arquivo não encontrado: {arquivo_origem}")
                falhas += 1
                continue

            # Valida e parseia todos os segmentos antes de iniciar
            segmentos = []
            erro = False
            for seg_str in segmentos_str:
                try:
                    inicio, fim = self._parsear_segmento(seg_str)
                    if fim <= inicio:
                        print(f"   ❌ Segmento inválido (fim <= início): {seg_str}")
                        erro = True
                        break
                    segmentos.append((inicio, fim, seg_str))
                except ValueError as e:
                    print(f"   ❌ {e}")
                    erro = True
                    break

            if erro:
                falhas += 1
                continue

            print(f"   Segmentos a manter: {len(segmentos)}")
            for i, (inicio, fim, seg_str) in enumerate(segmentos, 1):
                print(f"   {i}. {seg_str}  ({_formatar_tempo(fim - inicio)})")

            temp_dir = Path(tempfile.mkdtemp(prefix="fatiador_"))
            try:
                temp_files = []
                falha_extracao = False

                for i, (inicio, fim, seg_str) in enumerate(segmentos):
                    temp_out = temp_dir / f"seg_{i:03d}.mp4"
                    print(f"   ⏳ Segmento {i + 1}/{len(segmentos)}...", end=" ", flush=True)
                    if self._extrair_segmento(arquivo_origem, temp_out, inicio, fim):
                        print("ok")
                        temp_files.append(temp_out)
                    else:
                        print("falhou")
                        falha_extracao = True
                        break

                if falha_extracao:
                    print(f"   ❌ Falha na extração. Pulando.")
                    falhas += 1
                    continue

                arquivo_saida = self.pasta_saida / arquivo_origem.name
                print(f"   ⏳ Concatenando...", end=" ", flush=True)
                if self._concatenar(temp_files, arquivo_saida):
                    tamanho_mb = arquivo_saida.stat().st_size / (1024 * 1024)
                    print(f"ok  →  {arquivo_saida.name}  ({tamanho_mb:.1f} MB)")
                    processados += 1

                    if self.deletar_originais:
                        arquivo_origem.unlink()
                        print(f"   🗑️  Original removido.")
                else:
                    print("falhou")
                    falhas += 1

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

            print()

        print("=" * 60)
        print(f"✂️  Processados: {processados}")
        if falhas:
            print(f"❌ Falhas: {falhas}")
        print(f"📁 Saída: {self.pasta_saida}")
        print("=" * 60)

        return {"processados": processados, "falhas": falhas}
