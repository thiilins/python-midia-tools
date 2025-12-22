"""
Gerenciamento de barras de progresso padronizadas.
"""

from contextlib import contextmanager
from typing import Optional
from tqdm import tqdm


class ProgressBar:
    """
    Classe para gerenciar barras de progresso padronizadas.
    """

    def __init__(
        self,
        total: int,
        desc: str = "Processando",
        unit: str = "arquivo",
        postfix: Optional[dict] = None,
    ):
        """
        Inicializa a barra de progresso.

        Args:
            total: Número total de itens a processar.
            desc: Descrição da barra.
            unit: Unidade de medida.
            postfix: Dicionário com informações adicionais.
        """
        self.total = total
        self.desc = desc
        self.unit = unit
        self.postfix = postfix or {}
        self.pbar = None

    @contextmanager
    def context(self):
        """
        Context manager para usar a barra de progresso.

        Yields:
            tqdm: Objeto da barra de progresso.
        """
        self.pbar = tqdm(
            total=self.total,
            desc=self.desc,
            unit=self.unit,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )
        try:
            yield self.pbar
        finally:
            self.pbar.close()

    def update(self, n: int = 1):
        """Atualiza a barra de progresso."""
        if self.pbar:
            self.pbar.update(n)

    def set_postfix(self, postfix: dict):
        """Define informações adicionais na barra."""
        if self.pbar:
            self.pbar.set_postfix(postfix)

    def set_description(self, desc: str):
        """Define a descrição da barra."""
        if self.pbar:
            self.pbar.set_description(desc)
