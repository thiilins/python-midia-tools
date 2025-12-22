"""
Validações e verificações de dependências.
"""

import shutil
import sys


def verificar_ffmpeg() -> bool:
    """
    Verifica se FFmpeg e FFprobe estão instalados.

    Returns:
        bool: True se ambos estão disponíveis, False caso contrário.
    """
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    ffprobe_ok = shutil.which("ffprobe") is not None

    if not ffmpeg_ok:
        print("❌ ERRO: FFmpeg não encontrado no sistema.")
        print("   Instale o FFmpeg e adicione-o ao PATH.")
        print("   Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("   Linux: sudo apt-get install ffmpeg")
        print("   macOS: brew install ffmpeg")
        return False

    if not ffprobe_ok:
        print("⚠️  AVISO: FFprobe não encontrado.")
        print("   Algumas funcionalidades podem não funcionar.")
        print("   FFprobe geralmente vem junto com o FFmpeg.")

    return True


def verificar_pil() -> bool:
    """
    Verifica se Pillow está instalado.

    Returns:
        bool: True se Pillow está disponível, False caso contrário.
    """
    try:
        from PIL import Image

        return True
    except ImportError:
        print("❌ ERRO: Pillow não está instalado.")
        print("   Execute: pip install Pillow")
        return False


def verificar_opencv() -> bool:
    """
    Verifica se OpenCV está instalado.

    Returns:
        bool: True se OpenCV está disponível, False caso contrário.
    """
    try:
        import cv2

        return True
    except ImportError:
        print("❌ ERRO: OpenCV não está instalado.")
        print("   Execute: pip install opencv-python")
        return False


def verificar_dependencias_python() -> bool:
    """
    Verifica se todas as dependências Python estão instaladas.

    Returns:
        bool: True se todas estão disponíveis, False caso contrário.
    """
    try:
        import tqdm
        import numpy
        from PIL import Image

        return True
    except ImportError as e:
        missing = str(e).split()[-1] if hasattr(e, "name") and e.name else str(e)
        print(f"❌ ERRO: Dependência não encontrada: {missing}")
        print("   Execute: pip install -r requirements.txt")
        return False
