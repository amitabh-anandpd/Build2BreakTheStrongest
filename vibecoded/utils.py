"""
utils.py - Utility functions for the application
"""

import os
import re
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import json


# Logging setup
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Configure logging for the application"""
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    return logging.getLogger(__name__)


logger = setup_logging()


# File operations
def ensure_directory(path: str) -> str:
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def clean_directory(path: str, patterns: List[str] = None):
    """Clean temporary files from directory"""
    if not os.path.exists(path):
        return
    
    patterns = patterns or ['*.tmp', '*.temp']
    
    for pattern in patterns:
        for file_path in Path(path).glob(pattern):
            try:
                file_path.unlink()
                logger.debug(f"Deleted: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}: {e}")


def get_file_hash(file_path: str) -> str:
    """Get SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    return os.path.getsize(file_path) / (1024 * 1024)


# Text processing
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def extract_sentences(text: str, max_sentences: int = None) -> List[str]:
    """Extract sentences from text"""
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if max_sentences:
        sentences = sentences[:max_sentences]
    
    return sentences


def word_count(text: str) -> int:
    """Count words in text"""
    return len(text.split())


def estimate_reading_time(text: str, words_per_minute: int = 150) -> float:
    """Estimate reading time in minutes"""
    words = word_count(text)
    return words / words_per_minute


def estimate_speaking_time(text: str, words_per_minute: int = 150) -> float:
    """Estimate speaking time in seconds"""
    words = word_count(text)
    return (words / words_per_minute) * 60


# Video/Audio utilities
def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using FFmpeg"""
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return 0.0


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds"""
    return get_video_duration(audio_path)


def check_video_valid(video_path: str) -> bool:
    """Check if video file is valid"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', video_path],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# Progress tracking
class ProgressTracker:
    """Simple progress tracking for console output"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        
    def update(self, step_name: str = None):
        """Update progress"""
        self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        
        bar_length = 30
        filled_length = int(bar_length * self.current_step // self.total_steps)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        status = f"{self.description}: |{bar}| {percentage:.1f}%"
        if step_name:
            status += f" - {step_name}"
        
        print(f"\r{status}", end='', flush=True)
        
        if self.current_step >= self.total_steps:
            print()  # New line when complete
    
    def complete(self):
        """Mark as complete"""
        self.current_step = self.total_steps
        self.update()


# Validation
def validate_pdf_file(file_path: str) -> bool:
    """Validate PDF file"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    if not file_path.lower().endswith('.pdf'):
        logger.error(f"Not a PDF file: {file_path}")
        return False
    
    # Check file size
    size_mb = get_file_size_mb(file_path)
    if size_mb > 100:  # 100 MB limit
        logger.error(f"File too large: {size_mb:.2f} MB")
        return False
    
    # Check if file is readable
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                logger.error("Invalid PDF header")
                return False
    except Exception as e:
        logger.error(f"Cannot read file: {e}")
        return False
    
    return True


def validate_api_key(api_key: str) -> bool:
    """Basic validation of API key format"""
    if not api_key:
        return False
    
    # Basic checks
    if len(api_key) < 20:
        return False
    
    # Check for common placeholder values
    placeholders = ['your-api-key', 'xxx', 'api_key', 'key']
    if api_key.lower() in placeholders:
        return False
    
    return True


# Formatting utilities
def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


# Cache utilities
class SimpleCache:
    """Simple file-based cache for processed results"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        ensure_directory(str(self.cache_dir))
    
    def get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached value"""
        cache_path = self.get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, value: Dict):
        """Set cached value"""
        cache_path = self.get_cache_path(key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(value, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def clear(self):
        """Clear all cache"""
        clean_directory(str(self.cache_dir), ['*.json'])


# Error handling decorator
def handle_errors(default_return=None):
    """Decorator for error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator


# System checks
def system_check() -> Dict[str, bool]:
    """Check system requirements"""
    checks = {
        'ffmpeg': check_ffmpeg_installed(),
        'python_version': True,  # If this runs, Python is installed
    }
    
    # Check Python packages
    required_packages = [
        'PyPDF2', 'PIL', 'numpy', 
        'google.generativeai', 'gtts'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('.', '_').split('_')[0])
            checks[f'package_{package}'] = True
        except ImportError:
            checks[f'package_{package}'] = False
    
    return checks


def print_system_info():
    """Print system information and checks"""
    print("\n" + "="*60)
    print("System Check")
    print("="*60)
    
    checks = system_check()
    
    for check_name, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}: {'OK' if status else 'MISSING'}")
    
    all_ok = all(checks.values())
    
    print("="*60)
    if all_ok:
        print("✅ All system requirements met!")
    else:
        print("⚠️  Some requirements are missing. Please install them.")
    print("="*60 + "\n")
    
    return all_ok