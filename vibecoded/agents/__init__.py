"""
Agents package for PDF to YouTube Shorts conversion
"""

from .content_extractor import ContentExtractor
from .script_writer import ScriptWriter
from .visuals_maker import VisualsMaker
from .narrator import Narrator
from .video_composer import VideoComposer

__all__ = [
    'ContentExtractor',
    'ScriptWriter',
    'VisualsMaker',
    'Narrator',
    'VideoComposer'
]

__version__ = '1.0.0'