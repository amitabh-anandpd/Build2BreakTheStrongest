"""
agents/narrator.py
Generates narration audio from script using TTS
"""

import os
from typing import Dict, List
from gtts import gTTS
import subprocess


class Narrator:
    """Generates narration audio for video"""
    
    def __init__(self):
        self.output_dir = "temp_processing/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_audio(self, script: Dict) -> str:
        """
        Generate narration audio from script
        
        Args:
            script: Script dictionary with scenes
            
        Returns:
            Path to generated audio file
        """
        # Collect all narration text
        narration_parts = []
        
        # Add hook
        if 'hook' in script:
            narration_parts.append(script['hook'])
        
        # Add scene narrations
        for scene in script.get('scenes', []):
            narration = scene.get('narration', '')
            if narration:
                narration_parts.append(narration)
        
        # Add conclusion
        if 'conclusion' in script:
            narration_parts.append(script['conclusion'])
        
        # Add citation
        if 'source_title' in script:
            narration_parts.append(f"Source: {script['source_title']}")
        
        # Combine narration
        full_narration = ' '.join(narration_parts)
        
        print(f"Generating audio for {len(full_narration)} characters of narration...")
        
        # Generate audio using gTTS (Google Text-to-Speech)
        # For better quality, consider using: pyttsx3, edge-tts, or Coqui TTS
        output_path = os.path.join(self.output_dir, "narration.mp3")
        
        try:
            # Method 1: gTTS (simple, free, requires internet)
            tts = gTTS(text=full_narration, lang='en', slow=False)
            tts.save(output_path)
            
            # Optional: Adjust speed if needed using ffmpeg
            adjusted_path = os.path.join(self.output_dir, "narration_adjusted.mp3")
            try:
                subprocess.run([
                    'ffmpeg', '-i', output_path,
                    '-filter:a', 'atempo=1.1',  # 10% faster
                    '-vn', '-y',
                    adjusted_path
                ], check=True, capture_output=True)
                output_path = adjusted_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                # ffmpeg not available or failed, use original
                pass
            
        except Exception as e:
            print(f"TTS generation failed: {e}")
            # Fallback: create silent audio
            output_path = self._create_silent_audio(60)
        
        return output_path
    
    def _create_silent_audio(self, duration: int) -> str:
        """Create silent audio file as fallback"""
        output_path = os.path.join(self.output_dir, "narration.mp3")
        
        try:
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 
                f'anullsrc=r=44100:cl=stereo',
                '-t', str(duration),
                '-y', output_path
            ], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Can't create even silent audio
            pass
        
        return output_path
    
    def generate_scene_audios(self, script: Dict) -> Dict[int, str]:
        """
        Generate separate audio files for each scene (alternative approach)
        
        Args:
            script: Script dictionary
            
        Returns:
            Dictionary mapping scene numbers to audio file paths
        """
        audio_files = {}
        
        for scene in script.get('scenes', []):
            scene_num = scene.get('scene_number', 0)
            narration = scene.get('narration', '')
            
            if narration:
                output_path = os.path.join(self.output_dir, f"scene_{scene_num:02d}.mp3")
                
                try:
                    tts = gTTS(text=narration, lang='en', slow=False)
                    tts.save(output_path)
                    audio_files[scene_num] = output_path
                except Exception as e:
                    print(f"Failed to generate audio for scene {scene_num}: {e}")
        
        return audio_files