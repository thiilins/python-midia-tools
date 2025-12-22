"""
Conversor de WebP para JPG.
"""

from pathlib import Path
from typing import Tuple

from PIL import Image

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar


class ConversorWebP:
    """
    Classe para converter WebP para JPG com alta qualidade.
    """

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        qualidade: int = 100,
        apagar_original: bool = True,
        preservar_qualidade: bool = True,
        suporte_animacoes: bool = True,
    ):
        """
        Inicializa o conversor.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            qualidade: Qualidade JPG (0-100).
            apagar_original: Se True, deleta o arquivo WebP após converter.
            preservar_qualidade: Se True, analisa qualidade antes de converter.
            suporte_animacoes: Se True, converte WebP animado para GIF/MP4.
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("imagens")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.qualidade = qualidade
        self.apagar_original = apagar_original
        self.preservar_qualidade = preservar_qualidade
        self.suporte_animacoes = suporte_animacoes

    def _eh_animado(self, caminho: Path) -> bool:
        """
        Verifica se o WebP é animado.

        Args:
            caminho: Caminho do arquivo WebP.

        Returns:
            bool: True se for animado.
        """
        try:
            img = Image.open(caminho)
            if hasattr(img, "is_animated"):
                return img.is_animated
            # Verifica se tem múltiplos frames
            try:
                img.seek(1)
                return True
            except EOFError:
                return False
        except Exception:
            return False

    def _analisar_qualidade(self, caminho: Path) -> Tuple[int, dict]:
        """
        Analisa a qualidade da imagem WebP para determinar qualidade JPG ideal.

        Args:
            caminho: Caminho do arquivo WebP.

        Returns:
            Tuple[int, dict]: (qualidade_recomendada, info)
        """
        try:
            img = Image.open(caminho)
            tamanho_original = caminho.stat().st_size

            # Analisa resolução
            largura, altura = img.size
            megapixels = (largura * altura) / 1_000_000

            # Analisa modo de cor
            modo = img.mode
            tem_transparencia = modo in ("RGBA", "LA", "P")

            # Determina qualidade recomendada baseada em resolução
            if megapixels > 10:
                qualidade_rec = min(95, self.qualidade)  # Imagens grandes: alta qualidade
            elif megapixels > 5:
                qualidade_rec = min(90, self.qualidade)
            else:
                qualidade_rec = self.qualidade

            info = {
                "resolucao": f"{largura}x{altura}",
                "megapixels": megapixels,
                "modo": modo,
                "tem_transparencia": tem_transparencia,
                "tamanho_kb": tamanho_original / 1024,
            }

            return qualidade_rec, info
        except Exception:
            return self.qualidade, {}

    def _converter_animacao(self, caminho_entrada: Path, caminho_saida: Path) -> bool:
        """
        Converte WebP animado para GIF ou MP4.

        Args:
            caminho_entrada: Caminho do arquivo WebP animado.
            caminho_saida: Caminho do arquivo de saída.

        Returns:
            bool: True se a conversão foi bem-sucedida.
        """
        if not self.suporte_animacoes:
            return False

        # Tenta converter para GIF primeiro (mais simples)
        caminho_gif = caminho_saida.with_suffix(".gif")

        try:
            img = Image.open(caminho_entrada)
            frames = []
            try:
                while True:
                    frames.append(img.copy())
                    img.seek(img.tell() + 1)
            except EOFError:
                pass

            if frames:
                frames[0].save(
                    caminho_gif,
                    save_all=True,
                    append_images=frames[1:],
                    duration=img.info.get("duration", 100),
                    loop=img.info.get("loop", 0),
                )
                print(f"   🎬 Animação convertida para GIF: {caminho_gif.name}")
                return True
        except Exception as e:
            print(f"   ⚠️  Erro ao converter animação: {e}")
            return False

        return False

    def _converter_imagem(self, caminho_entrada: Path, caminho_saida: Path) -> Tuple[bool, str]:
        """
        Converte uma imagem WebP para JPG.

        Args:
            caminho_entrada: Caminho do arquivo WebP.
            caminho_saida: Caminho do arquivo JPG de saída.

        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Verifica se é animado
            if self._eh_animado(caminho_entrada):
                if self.suporte_animacoes:
                    if self._converter_animacao(caminho_entrada, caminho_saida):
                        return True, "animação convertida"
                    return False, "erro ao converter animação"
                return False, "WebP animado detectado (use suporte_animacoes=True)"

            # Analisa qualidade se solicitado
            qualidade_usar = self.qualidade
            info_qualidade = {}
            if self.preservar_qualidade:
                qualidade_usar, info_qualidade = self._analisar_qualidade(caminho_entrada)

            img = Image.open(caminho_entrada)

            # O WebP pode ter transparência (RGBA). O JPG não aceita (só RGB).
            if img.mode in ("RGBA", "LA"):
                # Cria um fundo branco
                fundo = Image.new(img.mode[:-1], img.size, (255, 255, 255))
                # Cola a imagem original por cima do fundo branco usando a máscara de transparência
                fundo.paste(img, img.split()[-1])
                img = fundo

            # Converte para RGB simples
            img = img.convert("RGB")

            # Salva como JPG com qualidade otimizada
            img.save(
                caminho_saida,
                "JPEG",
                quality=qualidade_usar,
                subsampling=0,  # Mantém fidelidade das cores
            )

            mensagem = ""
            if self.preservar_qualidade and info_qualidade:
                mensagem = f"Qualidade: {qualidade_usar}% (recomendada: {info_qualidade.get('resolucao', 'N/A')})"

            return True, mensagem
        except Exception as e:
            return False, str(e)

    def processar(self) -> dict:
        """
        Processa todos os arquivos WebP na pasta de entrada.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"sucessos": 0, "falhas": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        # Lista arquivos WebP
        arquivos = [
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() == ".webp"
        ]

        if not arquivos:
            print(f"ℹ️  Nenhum arquivo .webp encontrado em {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0}

        print(f"🚀 Encontrados {len(arquivos)} arquivo(s) WebP. Iniciando conversão...")
        print("-" * 60)

        sucessos = 0
        falhas = 0

        # Barra de progresso
        with ProgressBar(
            total=len(arquivos), desc="Convertendo", unit="arquivo"
        ).context() as pbar:
            for arquivo in arquivos:
                nome_jpg = arquivo.stem + ".jpg"
                caminho_destino = pasta_saida / nome_jpg

                sucesso, mensagem = self._converter_imagem(arquivo, caminho_destino)

                if sucesso:
                    if mensagem:
                        print(f"\n✅ {arquivo.name}: {mensagem}")
                    sucessos += 1
                    if self.apagar_original:
                        try:
                            arquivo.unlink()
                        except OSError:
                            pass
                else:
                    print(f"\n❌ {arquivo.name}: {mensagem}")
                    falhas += 1

                pbar.update(1)

        # Resumo Final
        print("\n" + "=" * 60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📁 Arquivos salvos em: {pasta_saida}")
        print("-" * 60)
        print("✨ Processo finalizado com sucesso!")

        return {"sucessos": sucessos, "falhas": falhas}
