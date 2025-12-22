"""
Módulo de processamento de imagens.
"""

from .optimizer import OtimizadorImagens
from .converter import ConversorWebP
from .validator import ValidadorImagens
from .duplicate_detector import DetectorDuplicatasImagens
from .ocr import OCRImagens
from .background_remover import RemovedorFundo
from .color_corrector import CorretorCores

__all__ = [
    "OtimizadorImagens",
    "ConversorWebP",
    "ValidadorImagens",
    "DetectorDuplicatasImagens",
    "OCRImagens",
    "RemovedorFundo",
    "CorretorCores",
]
