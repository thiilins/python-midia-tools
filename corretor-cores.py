#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corretor de Cores
================
Ajusta brilho, contraste, saturação e aplica filtros.
"""

import sys
from media_tools.image.color_corrector import CorretorCores


def main():
    """Função principal."""
    try:
        # Ajuste automático ativo, sem filtro específico
        corretor = CorretorCores(
            ajuste_automatico=True,
            brilho=1.0,
            contraste=1.0,
            saturacao=1.0,
            filtro=None,
        )
        corretor.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


