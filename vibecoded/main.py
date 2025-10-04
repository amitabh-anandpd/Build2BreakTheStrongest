"""
PDF to YouTube Shorts Converter
Main application file that orchestrates the entire pipeline
"""

import os
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json

@dataclass
class VideoConfig:
    """Configuration for video generation"""
    duration: int = 60  # seconds
    width: int = 1080
    height: int = 1920  # 9:16 aspect ratio for Shorts
    fps: int = 30
    style: str = "doodle"  # doodle, whiteboard, sketch


class PDFtoShortsConverter:
    """Main orchestrator for PDF to YouTube Shorts conversion"""
    
    def __init__(self, gemini_api_key: str, config: VideoConfig = None):
        self.gemini_api_key = gemini_api_key
        self.config = config or VideoConfig()
        self.temp_dir = "temp_processing"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def process_pdf(self, pdf_path: str, output_path: str = "output_short.mp4") -> str:
        """
        Main pipeline: PDF -> Text -> Script -> Visuals -> Video
        
        Args:
            pdf_path: Path to input PDF
            output_path: Path for output video
            
        Returns:
            Path to generated video
        """
        print("🚀 Starting PDF to YouTube Shorts conversion...")
        
        # Step 1: Extract content from PDF
        print("\n📄 Step 1: Extracting content from PDF...")
        from agents.content_extractor import ContentExtractor
        extractor = ContentExtractor()
        extracted_data = extractor.extract(pdf_path)
        
        # Step 2: Sanitize content (remove malicious content/prompt injections)
        print("\n🛡️ Step 2: Sanitizing content...")
        sanitized_text = self._sanitize_content(extracted_data['text'])
        sanitized_data = {
            **extracted_data,
            'text': sanitized_text
        }
        
        # Step 3: Generate script using Gemini
        print("\n✍️ Step 3: Generating video script with Gemini...")
        from agents.script_writer import ScriptWriter
        script_writer = ScriptWriter(self.gemini_api_key)
        script = script_writer.generate_script(
            sanitized_data, 
            max_duration=self.config.duration
        )
        
        # Step 4: Generate visuals
        print("\n🎨 Step 4: Creating doodle-style visuals...")
        from agents.visuals_maker import VisualsMaker
        visuals_maker = VisualsMaker(style=self.config.style)
        visual_assets = visuals_maker.generate_visuals(script)
        
        # Step 5: Generate narration audio
        print("\n🎙️ Step 5: Generating narration...")
        from agents.narrator import Narrator
        narrator = Narrator()
        audio_path = narrator.generate_audio(script)
        
        # Step 6: Compose final video
        print("\n🎬 Step 6: Composing final video...")
        from agents.video_composer import VideoComposer
        composer = VideoComposer(self.config)
        final_video = composer.compose(
            script=script,
            visual_assets=visual_assets,
            audio_path=audio_path,
            output_path=output_path,
            citations=extracted_data.get('citations', [])
        )
        
        print(f"\n✅ Video generated successfully: {final_video}")
        return final_video
    
    def _sanitize_content(self, text: str) -> str:
        """
        Remove malicious content and prompt injections
        
        Args:
            text: Raw extracted text
            
        Returns:
            Sanitized text
        """
        # Patterns to detect and remove
        malicious_patterns = [
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
        ]
        
        sanitized = text
        for pattern in malicious_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove excessive newlines and whitespace
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
        sanitized = re.sub(r' {2,}', ' ', sanitized)
        
        # Limit length to prevent DoS
        max_length = 50000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        
        return sanitized.strip()


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PDF to YouTube Shorts')
    parser.add_argument('pdf_path', help='Path to input PDF file')
    parser.add_argument('--output', default='output_short.mp4', help='Output video path')
    parser.add_argument('--api-key', required=True, help='Gemini API key')
    parser.add_argument('--duration', type=int, default=60, help='Video duration in seconds')
    parser.add_argument('--style', default='doodle', choices=['doodle', 'whiteboard', 'sketch'], 
                       help='Animation style')
    
    args = parser.parse_args()
    
    # Create configuration
    config = VideoConfig(
        duration=args.duration,
        style=args.style
    )
    
    # Initialize converter
    converter = PDFtoShortsConverter(
        gemini_api_key=args.api_key,
        config=config
    )
    
    # Process PDF
    output_video = converter.process_pdf(args.pdf_path, args.output)
    print(f"\n🎉 All done! Your YouTube Short is ready: {output_video}")


if __name__ == "__main__":
    main()