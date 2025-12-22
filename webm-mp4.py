#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONVERSOR WEBM → MP4 (Versão Otimizada)
=======================================
Converte .webm para .mp4 corrigindo timestamps,
frame rate variável e garantindo compatibilidade.
Ideal para conversão de capturas de tela e gravações web.
"""

import sys
import os
from media_tools.video.converter import ConversorWebM


def main():
    """Função principal."""
    # Verifica perfil via variável de ambiente ou argumento
    perfil = os.getenv("PERFIL_WEBM", None)

    if len(sys.argv) > 1:
        if sys.argv[1] in ["--web", "--mobile", "--archive"]:
            perfil = sys.argv[1].replace("--", "")

    try:
        conversor = ConversorWebM(
            manter_originais=True,
            corrigir_velocidade=False,
            fator_velocidade=2.0,
            fps_saida=30,
            qualidade_crf="20",
            perfil=perfil,
            detectar_problemas=True,
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
