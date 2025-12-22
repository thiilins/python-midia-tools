#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Imagens
====================
Script para validar se imagens são legíveis, separando em legíveis e ilegíveis.
"""

import sys
import os
from media_tools.image.validator import ValidadorImagens
from media_tools.common.validators import verificar_opencv


def main():
    """Função principal."""
    if not verificar_opencv():
        sys.exit(1)

    # Verifica se deve gerar relatório HTML (via variável de ambiente ou argumento)
    gerar_html = os.getenv("GERAR_RELATORIO_HTML", "false").lower() == "true"

    # Verifica argumentos da linha de comando
    if len(sys.argv) > 1 and sys.argv[1] in ["--html", "-h"]:
        gerar_html = True

    try:
        validador = ValidadorImagens(gerar_relatorio_html=gerar_html)
        validador.processar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
