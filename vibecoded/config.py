"""
config.py - Configuration settings for the application
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class AppConfig:
    """Application-wide configuration"""
    
    # API Keys
    gemini_api_key: str = field(default_factory=lambda: os.environ.get('GEMINI_API_KEY', ''))
    
    # Paths
    temp_dir: str = "temp_processing"
    output_dir: str = "output_videos"
    
    # Processing
    max_pdf_size_mb: int = 50
    max_text_length: int = 50000
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "pdf_to_shorts.log"


@dataclass
class VideoConfig:
    """Video generation configuration"""
    
    # Video specifications
    duration: int = 60  # seconds
    width: int = 1080
    height: int = 1920  # 9:16 aspect ratio for Shorts
    fps: int = 30
    
    # Visual style
    style: str = "doodle"  # doodle, whiteboard, sketch
    background_color: str = "white"
    
    # Animation settings
    transition_duration: float = 0.5  # seconds
    default_animation: str = "draw_on"
    
    # Audio settings
    audio_bitrate: str = "128k"
    audio_sample_rate: int = 44100
    
    # Quality settings
    video_codec: str = "libx264"
    video_preset: str = "medium"  # ultrafast, fast, medium, slow
    crf: int = 23  # 0-51, lower = better quality


@dataclass
class ScriptConfig:
    """Script generation configuration"""
    
    # Script parameters
    max_scenes: int = 7
    min_scene_duration: int = 8
    max_scene_duration: int = 12
    
    # Content preferences
    tone: str = "conversational"  # conversational, professional, casual, energetic
    include_hook: bool = True
    include_conclusion: bool = True
    include_citations: bool = True
    
    # Gemini settings
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class VisualsConfig:
    """Visual generation configuration"""
    
    # Drawing settings
    line_width: int = 4
    sketch_iterations: int = 3  # For sketchy effect
    
    # Colors (RGB tuples)
    primary_color: tuple = (0, 0, 0)  # Black
    secondary_color: tuple = (100, 100, 100)  # Gray
    accent_color: tuple = (255, 100, 100)  # Red accent
    
    # Text settings
    title_font_size: int = 80
    subtitle_font_size: int = 50
    body_font_size: int = 40
    
    # Effects
    add_noise: bool = True
    noise_intensity: int = 10
    add_texture: bool = True


@dataclass
class SecurityConfig:
    """Security and sanitization configuration"""
    
    # Content filtering
    enable_sanitization: bool = True
    max_input_length: int = 50000
    
    # Malicious patterns to detect
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r'ignore\s+(previous|all|above)\s+instructions',
        r'disregard\s+.{0,20}instructions',
        r'system\s*[:]\s*you\s+are',
        r'<\s*script\s*>',
        r'javascript\s*:',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__',
        r'subprocess',
        r'os\.system',
    ])
    
    # Rate limiting
    enable_rate_limit: bool = False
    max_requests_per_hour: int = 10


# Preset configurations for different use cases

PRESETS: Dict[str, Dict] = {
    "quick": {
        "video": VideoConfig(
            duration=30,
            fps=24,
            video_preset="ultrafast",
            crf=28
        ),
        "script": ScriptConfig(
            max_scenes=4,
            tone="casual"
        )
    },
    
    "standard": {
        "video": VideoConfig(
            duration=60,
            fps=30,
            video_preset="medium",
            crf=23
        ),
        "script": ScriptConfig(
            max_scenes=7,
            tone="conversational"
        )
    },
    
    "high_quality": {
        "video": VideoConfig(
            duration=60,
            fps=60,
            video_preset="slow",
            crf=18
        ),
        "script": ScriptConfig(
            max_scenes=8,
            tone="professional",
            temperature=0.5
        )
    },
    
    "educational": {
        "video": VideoConfig(
            duration=90,
            style="whiteboard",
            fps=30
        ),
        "script": ScriptConfig(
            max_scenes=9,
            tone="professional",
            include_citations=True
        )
    },
    
    "viral": {
        "video": VideoConfig(
            duration=45,
            style="doodle",
            fps=30
        ),
        "script": ScriptConfig(
            max_scenes=6,
            tone="energetic",
            include_hook=True,
            temperature=0.9
        )
    }
}


def get_preset_config(preset_name: str) -> tuple:
    """
    Get preset configuration
    
    Args:
        preset_name: Name of preset (quick, standard, high_quality, educational, viral)
        
    Returns:
        Tuple of (VideoConfig, ScriptConfig)
    """
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")
    
    preset = PRESETS[preset_name]
    return preset.get("video", VideoConfig()), preset.get("script", ScriptConfig())


def load_config_from_file(config_path: str) -> AppConfig:
    """
    Load configuration from JSON or YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        AppConfig instance
    """
    import json
    
    with open(config_path, 'r') as f:
        if config_path.endswith('.json'):
            config_dict = json.load(f)
        elif config_path.endswith(('.yaml', '.yml')):
            import yaml
            config_dict = yaml.safe_load(f)
        else:
            raise ValueError("Config file must be JSON or YAML")
    
    return AppConfig(**config_dict)


# Default configurations
DEFAULT_APP_CONFIG = AppConfig()
DEFAULT_VIDEO_CONFIG = VideoConfig()
DEFAULT_SCRIPT_CONFIG = ScriptConfig()
DEFAULT_VISUALS_CONFIG = VisualsConfig()
DEFAULT_SECURITY_CONFIG = SecurityConfig()