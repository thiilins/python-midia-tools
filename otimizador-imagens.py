#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador e Conversor de Imagens
=================================
Script para:
1. Converter automaticamente WebP para JPG.
2. Otimizar JPG, JPEG e PNG (redução de tamanho).
3. Barra de progresso em tempo real.
"""

import sys
from media_tools.image.optimizer import OtimizadorImagens
from media_tools.common.validators import verificar_pil


def main():
    """Função principal."""
    if not verificar_pil():
        sys.exit(1)

    try:
        otimizador = OtimizadorImagens(qualidade_jpg=85)
        otimizador.processar(deletar_originais=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
