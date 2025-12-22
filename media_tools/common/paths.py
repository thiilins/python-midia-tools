"""
Gerenciamento de caminhos e pastas.
"""

import os
from pathlib import Path
from typing import Tuple


def obter_diretorio_base() -> Path:
    """
    Retorna o diretório base do projeto.

    Returns:
        Path: Caminho absoluto do diretório base.
    """
    return Path(__file__).parent.parent.parent.resolve()


def obter_pastas_entrada_saida(tipo_media: str = "imagens") -> Tuple[Path, Path]:
    """
    Obtém os caminhos das pastas de entrada e saída.

    Args:
        tipo_media: Tipo de mídia ('imagens' ou 'videos').

    Returns:
        Tuple[Path, Path]: (pasta_entrada, pasta_saida)
    """
    base = obter_diretorio_base()
    entrada = base / "entrada" / tipo_media
    saida = base / "saida" / tipo_media
    return entrada, saida


def criar_pastas(
    pasta_entrada: Path, pasta_saida: Path, criar_entrada: bool = True
) -> bool:
    """
    Cria as pastas necessárias se não existirem.

    Args:
        pasta_entrada: Caminho da pasta de entrada.
        pasta_saida: Caminho da pasta de saída.
        criar_entrada: Se True, cria a pasta de entrada se não existir.

    Returns:
        bool: True se as pastas existem/foram criadas, False caso contrário.
    """
    try:
        if criar_entrada and not pasta_entrada.exists():
            pasta_entrada.mkdir(parents=True, exist_ok=True)
            print(f"✅ Pasta de entrada criada: {pasta_entrada}")
            print(f"📁 Coloque seus arquivos nela e execute o script novamente.")
            return False

        pasta_saida.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        print(f"❌ Erro ao criar pastas: {e}")
        return False
