"""
Corretor de cores e filtros de imagens.
"""

import numpy as np
from pathlib import Path
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar


class CorretorCores:
    """
    Classe para correção de cores e aplicação de filtros.
    """

    EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        ajuste_automatico: bool = True,
        brilho: float = 1.0,
        contraste: float = 1.0,
        saturacao: float = 1.0,
        filtro: str = None,
    ):
        """
        Inicializa o corretor.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            ajuste_automatico: Se True, aplica ajuste automático.
            brilho: Fator de brilho (0.5-2.0, 1.0 = normal).
            contraste: Fator de contraste (0.5-2.0, 1.0 = normal).
            saturacao: Fator de saturação (0.0-2.0, 1.0 = normal).
            filtro: Filtro a aplicar ('sepia', 'bw', 'vintage', None).
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("imagens")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or (Path(saida).parent / "corrigidas")
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.ajuste_automatico = ajuste_automatico
        self.brilho = brilho
        self.contraste = contraste
        self.saturacao = saturacao
        self.filtro = filtro

    def _aplicar_filtro(self, img: Image.Image, filtro_nome: str) -> Image.Image:
        """
        Aplica filtro à imagem.

        Args:
            img: Imagem PIL.
            filtro_nome: Nome do filtro.

        Returns:
            Image: Imagem com filtro aplicado.
        """
        if filtro_nome == "sepia":
            # Converte para sépia
            img_array = np.array(img.convert("RGB"))
            sepia = np.array([[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]])
            img_sepia = np.dot(img_array, sepia.T).clip(0, 255).astype(np.uint8)
            return Image.fromarray(img_sepia)
        elif filtro_nome == "bw":
            # Preto e branco
            return img.convert("L").convert("RGB")
        elif filtro_nome == "vintage":
            # Efeito vintage (sépia + contraste)
            img_sepia = self._aplicar_filtro(img, "sepia")
            enhancer = ImageEnhance.Contrast(img_sepia)
            return enhancer.enhance(1.2)
        return img

    def _corrigir_olhos_vermelhos(self, img: Image.Image) -> Image.Image:
        """
        Corrige olhos vermelhos (simplificado - reduz vermelho em áreas específicas).

        Args:
            img: Imagem PIL.

        Returns:
            Image: Imagem corrigida.
        """
        # Implementação simplificada - reduz saturação de vermelho
        img_array = np.array(img.convert("RGB"))
        # Reduz intensidade de vermelho em pixels muito vermelhos
        mask = img_array[:, :, 0] > 150
        img_array[mask, 0] = np.clip(img_array[mask, 0] * 0.7, 0, 255)
        return Image.fromarray(img_array.astype(np.uint8))

    def _processar_imagem(self, caminho_entrada: Path, caminho_saida: Path) -> bool:
        """
        Processa uma imagem aplicando correções.

        Args:
            caminho_entrada: Caminho da imagem de entrada.
            caminho_saida: Caminho da imagem de saída.

        Returns:
            bool: True se o processamento foi bem-sucedido.
        """
        try:
            img = Image.open(caminho_entrada)

            # Converte para RGB se necessário
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Ajuste automático
            if self.ajuste_automatico:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.1)  # Aumenta brilho levemente
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)  # Aumenta contraste levemente

            # Ajustes manuais
            if self.brilho != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(self.brilho)

            if self.contraste != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(self.contraste)

            if self.saturacao != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(self.saturacao)

            # Aplica filtro
            if self.filtro:
                img = self._aplicar_filtro(img, self.filtro)

            # Corrige olhos vermelhos (sempre aplica se detectar)
            img = self._corrigir_olhos_vermelhos(img)

            # Salva
            img.save(caminho_saida, quality=95, optimize=True)
            return True
        except Exception as e:
            print(f"   ⚠️  Erro: {e}")
            return False

    def processar(self) -> dict:
        """
        Processa todas as imagens na pasta de entrada.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"sucessos": 0, "falhas": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = [
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print(f"ℹ️  Nenhuma imagem encontrada em {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0}

        print(f"🚀 Corrigindo cores de {len(arquivos)} imagem(ns)...")
        print(
            f"⚙️  Ajuste automático: {'Sim' if self.ajuste_automatico else 'Não'} | "
            f"Filtro: {self.filtro or 'Nenhum'}"
        )
        print("-" * 60)

        sucessos = 0
        falhas = 0

        with ProgressBar(
            total=len(arquivos), desc="Corrigindo", unit="img"
        ).context() as pbar:
            for arquivo in arquivos:
                caminho_saida = pasta_saida / arquivo.name

                if self._processar_imagem(arquivo, caminho_saida):
                    sucessos += 1
                else:
                    falhas += 1

                pbar.update(1)

        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📁 Arquivos salvos em: {pasta_saida}")
        print("-" * 60)

        return {"sucessos": sucessos, "falhas": falhas}


