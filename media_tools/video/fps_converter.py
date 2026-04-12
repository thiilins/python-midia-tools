"""
Conversor de FPS — reduz framerate de vídeos (ex: 60fps → 30fps).

60fps → 30fps reduz ~30-40% do tamanho antes de qualquer compressão.
Útil como pré-processamento antes do compressor H.265.
"""

import subprocess
from pathlib import Path

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg
from ..common.resource_control import obter_configuracao_threads


class ConversorFPS:
    """
    Converte framerate de vídeos via re-encode H.264.

    Vídeos com FPS <= fps_alvo são pulados automaticamente.
    Saída em H.264 CRF 16 (alta qualidade) — adequado para uso
    posterior com o compressor H.265.
    """

    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov", ".webm", ".avi", ".mkv"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        fps_alvo: int = 30,
        crf: int = 16,
        deletar_originais: bool = False,
    ):
        """
        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            fps_alvo: FPS de destino (padrão: 30).
            crf: Qualidade H.264 (padrão: 16 = alta qualidade).
            deletar_originais: Remove originais após conversão (padrão: False).
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = Path(pasta_entrada)
            self.pasta_saida = Path(pasta_saida)

        self.fps_alvo = fps_alvo
        self.crf = crf
        self.deletar_originais = deletar_originais
        self.threads = obter_configuracao_threads()

    def _obter_fps(self, arquivo: Path) -> float:
        """Obtém FPS atual do vídeo via ffprobe."""
        comando = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(arquivo),
        ]
        try:
            resultado = subprocess.run(
                comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=15
            )
            fps_str = resultado.stdout.strip()
            if "/" in fps_str:
                num, den = fps_str.split("/")
                return float(num) / float(den) if float(den) else 0.0
            return float(fps_str)
        except Exception:
            return 0.0

    def _converter(self, arquivo_entrada: Path, arquivo_saida: Path) -> bool:
        """
        Converte FPS do vídeo.

        Usa filtro fps= para re-samplar frames, H.264 CRF 16 para
        manter qualidade alta (adequado como intermediate antes de H.265).
        Áudio copiado sem re-encode.
        """
        comando = [
            "ffmpeg", "-y",
            "-i", str(arquivo_entrada),
            "-vf", f"fps={self.fps_alvo}",
            "-c:v", "libx264",
            "-crf", str(self.crf),
            "-preset", "medium",
            "-c:a", "copy",
            "-threads", str(self.threads),
            str(arquivo_saida),
        ]
        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=7200,
            )
            return resultado.returncode == 0 and arquivo_saida.exists()
        except Exception:
            return False

    def processar(self) -> dict:
        """
        Processa todos os vídeos na pasta de entrada.

        Vídeos com FPS já igual ou inferior ao fps_alvo são pulados.

        Returns:
            dict: {"sucessos": N, "falhas": N, "pulados": N}
        """
        if not verificar_ffmpeg():
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = [
            f for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print(f"ℹ️  Nenhum vídeo encontrado em {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        print(f"🚀 Convertendo FPS → {self.fps_alvo}fps ({len(arquivos)} vídeo(s))")
        print(f"⚙️  CRF: {self.crf} (H.264 alta qualidade) | Threads: {self.threads}")
        print(f"💡 Pré-processamento: use compressor H.265 na sequência para menor arquivo")
        print("-" * 60)

        sucessos = 0
        falhas = 0
        pulados = 0

        with ProgressBar(
            total=len(arquivos), desc="Convertendo FPS", unit="vídeo"
        ).context() as pbar:
            for arquivo in arquivos:
                fps_atual = self._obter_fps(arquivo)

                # Pula se já está no FPS alvo (tolerância de 0.5fps)
                if fps_atual > 0 and fps_atual <= self.fps_alvo + 0.5:
                    fps_str = f"{fps_atual:.0f}" if fps_atual == int(fps_atual) else f"{fps_atual:.1f}"
                    print(f"\n⏭️  {arquivo.name} — já em {fps_str}fps, pulado")
                    pulados += 1
                    pbar.update(1)
                    continue

                fps_str = f"{fps_atual:.0f}" if fps_atual > 0 else "?"
                nome_saida = f"{arquivo.stem}_{self.fps_alvo}fps.mp4"
                arquivo_saida = pasta_saida / nome_saida

                print(f"\n⚙️  {arquivo.name}  ({fps_str}fps → {self.fps_alvo}fps)...")

                if self._converter(arquivo, arquivo_saida):
                    orig_mb = arquivo.stat().st_size / (1024 * 1024)
                    novo_mb = arquivo_saida.stat().st_size / (1024 * 1024)
                    reducao = (1 - novo_mb / orig_mb) * 100 if orig_mb > 0 else 0
                    print(
                        f"✅ {nome_saida}  "
                        f"{orig_mb:.0f}MB → {novo_mb:.0f}MB  "
                        f"({reducao:.0f}% menor)"
                    )
                    sucessos += 1

                    if self.deletar_originais:
                        arquivo.unlink()
                        print(f"   🗑️  Original removido: {arquivo.name}")
                else:
                    print(f"❌ Erro ao converter {arquivo.name}")
                    falhas += 1

                pbar.update(1)

        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("-" * 60)
        print(f"✅ Convertidos: {sucessos}")
        print(f"⏭️  Pulados (já em ≤{self.fps_alvo}fps): {pulados}")
        if falhas:
            print(f"❌ Falhas: {falhas}")
        print(f"📁 Arquivos em: {pasta_saida}")
        if sucessos > 0:
            print(f"💡 Próximo passo: python otimizador-compressor-video.py --preset stream_720p")
        print("-" * 60)

        return {"sucessos": sucessos, "falhas": falhas, "pulados": pulados}
