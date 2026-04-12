"""
Cortador de vídeos — extrai segmentos por timestamp em copy mode.
Copy mode = sem re-encode, instantâneo mesmo em arquivos de 15GB.
"""

import subprocess
from pathlib import Path
from typing import Optional

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.validators import verificar_ffmpeg


def _converter_tempo(s: str) -> float:
    """Converte HH:MM:SS, MM:SS ou segundos para float."""
    s = s.strip()
    partes = s.split(":")
    try:
        if len(partes) == 3:
            return int(partes[0]) * 3600 + int(partes[1]) * 60 + float(partes[2])
        elif len(partes) == 2:
            return int(partes[0]) * 60 + float(partes[1])
        else:
            return float(s)
    except ValueError:
        raise ValueError(f"Formato inválido: '{s}'. Use HH:MM:SS, MM:SS ou segundos.")


def _formatar_tempo(segundos: float) -> str:
    """Converte segundos para HH:MM:SS."""
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = segundos % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


class CortadorVideo:
    """
    Extrai segmentos de vídeo por timestamp usando copy mode.

    Copy mode = sem re-encode = processamento instantâneo,
    sem perda de qualidade, independente do tamanho do arquivo.

    Uso interativo: processar() exibe lista de vídeos e pede timestamps.
    """

    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov", ".webm", ".avi", ".mkv"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
    ):
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or (Path(saida).parent / "clips")
        else:
            self.pasta_entrada = Path(pasta_entrada)
            self.pasta_saida = Path(pasta_saida)

    def _obter_duracao(self, arquivo: Path) -> float:
        """Obtém duração do vídeo em segundos via ffprobe."""
        comando = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(arquivo),
        ]
        try:
            resultado = subprocess.run(
                comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=30
            )
            return float(resultado.stdout.strip())
        except Exception:
            return 0.0

    def _listar_videos(self) -> list:
        pasta = Path(self.pasta_entrada).resolve()
        return sorted([
            f for f in pasta.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ])

    def _cortar(
        self,
        arquivo_entrada: Path,
        arquivo_saida: Path,
        inicio: float,
        fim: float,
    ) -> bool:
        """
        Extrai segmento em copy mode.

        Usa -ss antes de -i (seek rápido) + -t para duração.
        -avoid_negative_ts make_zero corrige timestamps do clip.
        """
        duracao = fim - inicio
        comando = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-i", str(arquivo_entrada),
            "-t", str(duracao),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            str(arquivo_saida),
        ]
        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3600,
            )
            return resultado.returncode == 0 and arquivo_saida.exists()
        except Exception:
            return False

    def cortar_arquivo(
        self,
        arquivo: Path,
        inicio: float,
        fim: float,
        sufixo: str = "clip",
    ) -> Optional[Path]:
        """
        Corta um segmento de um arquivo específico.

        Args:
            arquivo: Caminho do vídeo de entrada.
            inicio: Início do segmento em segundos.
            fim: Fim do segmento em segundos.
            sufixo: Sufixo do nome do arquivo de saída.

        Returns:
            Path do arquivo criado, ou None em caso de falha.
        """
        pasta_saida = Path(self.pasta_saida).resolve()
        pasta_saida.mkdir(parents=True, exist_ok=True)

        nome_saida = f"{arquivo.stem}_{sufixo}.mp4"
        arquivo_saida = pasta_saida / nome_saida

        if self._cortar(arquivo, arquivo_saida, inicio, fim):
            return arquivo_saida
        return None

    def processar(self) -> dict:
        """
        Modo interativo: lista vídeos disponíveis e solicita timestamps
        via input(). Permite cortar múltiplos segmentos em sequência.

        Returns:
            dict: {"clips": N, "falhas": N}
        """
        if not verificar_ffmpeg():
            return {"clips": 0, "falhas": 0}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"clips": 0, "falhas": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = self._listar_videos()
        if not arquivos:
            print(f"ℹ️  Nenhum vídeo encontrado em {pasta_entrada}")
            return {"clips": 0, "falhas": 0}

        print("\n" + "=" * 60)
        print("✂️   CORTADOR DE VÍDEO — COPY MODE")
        print("=" * 60)
        print("Formatos: HH:MM:SS  |  MM:SS  |  segundos")
        print("Copy mode = sem re-encode, instantâneo\n")

        print("Vídeos disponíveis:")
        for i, arq in enumerate(arquivos, 1):
            duracao = self._obter_duracao(arq)
            dur_str = f"  [{_formatar_tempo(duracao)}]" if duracao > 0 else ""
            print(f"  {i:2d}. {arq.name}{dur_str}")

        clips = 0
        falhas = 0

        print()
        while True:
            try:
                escolha = input("Número do vídeo (ou 'q' para sair): ").strip()
                if escolha.lower() in ("q", ""):
                    break

                idx = int(escolha) - 1
                if idx < 0 or idx >= len(arquivos):
                    print("  ❌ Número inválido.\n")
                    continue

                arquivo = arquivos[idx]
                duracao_total = self._obter_duracao(arquivo)
                print(f"\n  📹 {arquivo.name} — {_formatar_tempo(duracao_total)}")

                inicio_str = input("  Início (ex: 00:10:30): ").strip()
                fim_str = input("  Fim    (ex: 00:45:00): ").strip()

                inicio = _converter_tempo(inicio_str)
                fim = _converter_tempo(fim_str)

                if fim <= inicio:
                    print("  ❌ Fim deve ser maior que início.\n")
                    continue

                if duracao_total > 0 and fim > duracao_total:
                    print(f"  ⚠️  Ajustado fim para {_formatar_tempo(duracao_total)}")
                    fim = duracao_total

                sufixo = input("  Sufixo do arquivo [clip]: ").strip() or "clip"
                nome_saida = f"{arquivo.stem}_{sufixo}.mp4"
                arquivo_saida = pasta_saida / nome_saida

                duracao_clip = fim - inicio
                print(f"\n  ⏳ Cortando {_formatar_tempo(inicio)} → {_formatar_tempo(fim)} ({_formatar_tempo(duracao_clip)})...")

                if self._cortar(arquivo, arquivo_saida, inicio, fim):
                    tamanho_mb = arquivo_saida.stat().st_size / (1024 * 1024)
                    print(f"  ✅ {nome_saida}  ({tamanho_mb:.1f} MB)")
                    clips += 1
                else:
                    print("  ❌ Falha ao cortar.")
                    falhas += 1

                outro = input("\n  Cortar outro segmento? (s/N): ").strip().lower()
                if outro != "s":
                    break
                print()

            except (ValueError, KeyboardInterrupt) as e:
                if isinstance(e, KeyboardInterrupt):
                    print("\n\n⚠️  Interrompido.")
                    break
                print(f"  ❌ {e}\n")

        print("\n" + "=" * 60)
        print(f"✂️  Clips criados: {clips}")
        if falhas:
            print(f"❌ Falhas: {falhas}")
        print(f"📁 Clips em: {pasta_saida}")
        print("=" * 60)

        return {"clips": clips, "falhas": falhas}
