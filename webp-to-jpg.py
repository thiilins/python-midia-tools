#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor WebP para JPG
=======================
Converte arquivos WebP para JPG com qualidade máxima.
Suporta WebP animado (converte para GIF).
"""

import sys
from media_tools.image.converter import ConversorWebP
from media_tools.common.validators import verificar_pil


def main():
    """Função principal."""
    if not verificar_pil():
        sys.exit(1)

    try:
        conversor = ConversorWebP(
            qualidade=100,
            apagar_original=True,
            preservar_qualidade=True,
            suporte_animacoes=True,
        )
        conversor.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
