"""
Módulo de processamento de vídeos.
"""

from .optimizer import OtimizadorVideo
from .converter import ConversorWebM
from .extractor import ExtratorAudio, ExtratorThumbnails
from .merger import MergerVideos
from .stabilizer import EstabilizadorVideo
from .duplicate_detector import DetectorDuplicatasVideos

__all__ = [
    "OtimizadorVideo",
    "ConversorWebM",
    "ExtratorAudio",
    "ExtratorThumbnails",
    "MergerVideos",
    "EstabilizadorVideo",
    "DetectorDuplicatasVideos",
]
