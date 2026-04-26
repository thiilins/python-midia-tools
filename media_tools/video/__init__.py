"""
Módulo de processamento de vídeos.
"""

from .optimizer import OtimizadorVideo
from .compressor import CompressorVideo
from .converter import ConversorWebM
from .extractor import ExtratorAudio, ExtratorThumbnails
from .merger import MergerVideos
from .stabilizer import EstabilizadorVideo
from .duplicate_detector import DetectorDuplicatasVideos
from .corrector import CorretorVideo
from .cutter import CortadorVideo
from .analyzer import AnalisadorMidia
from .fps_converter import ConversorFPS
from .slicer import FatiadorVideo
from .clipper import ClipperVideo
from .web_compressor import CompressorWebVideo

__all__ = [
    "OtimizadorVideo",
    "CompressorVideo",
    "ConversorWebM",
    "ExtratorAudio",
    "ExtratorThumbnails",
    "MergerVideos",
    "EstabilizadorVideo",
    "DetectorDuplicatasVideos",
    "CorretorVideo",
    "CortadorVideo",
    "AnalisadorMidia",
    "ConversorFPS",
    "FatiadorVideo",
    "ClipperVideo",
    "CompressorWebVideo",
]
