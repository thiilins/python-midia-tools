#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Removedor de Fundo
==================
Remove fundo de imagens automaticamente usando IA.
"""

import sys
from media_tools.image.background_remover import RemovedorFundo


def main():
    """Função principal."""
    try:
        removedor = RemovedorFundo()
        removedor.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

