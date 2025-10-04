"""
agents/video_composer.py
Composes final video using FFmpeg with animations and effects
"""

import os
import subprocess
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont
import json


class VideoComposer:
    """Composes final video with animations, audio, and citations"""
    
    def __init__(self, config):
        self.config = config
        self.temp_dir = "temp_processing/video"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def compose(self, script: Dict, visual_assets: Dict, 
                audio_path: str, output_path: str, citations: List[Dict]) -> str:
        """
        Compose final video with all elements
        
        Args:
            script: Script dictionary
            visual_assets: Dictionary of visual asset paths
            audio_path: Path to narration audio
            output_path: Output video path
            citations: List of citation dictionaries
            
        Returns:
            Path to final video
        """
        print("Composing final video...")
        
        # Step 1: Create animated sequences for each scene
        scene_videos = self._create_scene_animations(script, visual_assets)
        
        # Step 2: Add intro and outro
        intro_video = self._create_intro(script)
        outro_video = self._create_outro(script, citations)
        
        # Step 3: Concatenate all scenes
        all_videos = [intro_video] + scene_videos + [outro_video]
        concat_video = self._concatenate_videos(all_videos)
        
        # Step 4: Add audio
        final_video = self._add_audio(concat_video, audio_path, output_path)
        
        print(f"Video composition complete: {final_video}")
        return final_video
    
    def _create_scene_animations(self, script: Dict, visual_assets: Dict) -> List[str]:
        """Create animated video clips for each scene"""
        scene_videos = []
        
        for scene in script.get('scenes', []):
            scene_num = scene.get('scene_number', 0)
            duration = scene.get('duration', 10)
            animation_type = scene.get('animation_type', 'draw_on')
            
            if scene_num not in visual_assets:
                continue
            
            asset = visual_assets[scene_num]
            image_path = asset['path']
            
            # Create animated video from static image
            video_path = os.path.join(self.temp_dir, f"scene_{scene_num:02d}.mp4")
            
            if animation_type == 'draw_on':
                self._create_draw_on_animation(image_path, video_path, duration)
            elif animation_type == 'zoom':
                self._create_zoom_animation(image_path, video_path, duration)
            elif animation_type == 'fade_in':
                self._create_fade_animation(image_path, video_path, duration)
            else:
                self._create_simple_video(image_path, video_path, duration)
            
            scene_videos.append(video_path)
        
        return scene_videos
    
    def _create_draw_on_animation(self, image_path: str, output_path: str, duration: int):
        """Create 'drawing on' animation effect"""
        
        # Use FFmpeg with custom filter to simulate drawing effect
        # This creates a reveal animation from top to bottom
        try:
            subprocess.run([
                'ffmpeg',
                '-loop', '1',
                '-i', image_path,
                '-vf', f"crop=iw:ih*t/{duration}:0:0,pad=iw:ih:0:(oh-ih)/2:white",
                '-t', str(duration),
                '-r', str(self.config.fps),
                '-pix_fmt', 'yuv420p',
                '-y', output_path
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Fallback to simple video
            self._create_simple_video(image_path, output_path, duration)
    
    def _create_zoom_animation(self, image_path: str, output_path: str, duration: int):
        """Create zoom-in animation"""
        
        try:
            subprocess.run([
                'ffmpeg',
                '-loop', '1',
                '-i', image_path,
                '-vf', f"scale=iw*1.2:ih*1.2,zoompan=z='min(zoom+0.0015,1.2)':d={duration * self.config.fps}:s={self.config.width}x{self.config.height}",
                '-t', str(duration),
                '-r', str(self.config.fps),
                '-pix_fmt', 'yuv420p',
                '-y', output_path
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self._create_simple_video(image_path, output_path, duration)
    
    def _create_fade_animation(self, image_path: str, output_path: str, duration: int):
        """Create fade-in animation"""
        
        try:
            subprocess.run([
                'ffmpeg',
                '-loop', '1',
                '-i', image_path,
                '-vf', f"fade=t=in:st=0:d=1",
                '-t', str(duration),
                '-r', str(self.config.fps),
                '-pix_fmt', 'yuv420p',
                '-y', output_path
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self._create_simple_video(image_path, output_path, duration)
    
    def _create_simple_video(self, image_path: str, output_path: str, duration: int):
        """Create simple static video from image"""
        
        subprocess.run([
            'ffmpeg',
            '-loop', '1',
            '-i', image_path,
            '-t', str(duration),
            '-r', str(self.config.fps),
            '-pix_fmt', 'yuv420p',
            '-y', output_path
        ], check=True, capture_output=True)
    
    def _create_intro(self, script: Dict) -> str:
        """Create intro sequence"""
        
        # Create intro image
        img = Image.new('RGB', (self.config.width, self.config.height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add title
        title = script.get('title', 'Video')
        hook = script.get('hook', '')
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            hook_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
        except:
            title_font = ImageFont.load_default()
            hook_font = ImageFont.load_default()
        
        # Draw title
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.config.width - text_width) // 2
        y = self.config.height // 3
        
        # Add shadow effect
        draw.text((x+3, y+3), title, fill=(200, 200, 200), font=title_font)
        draw.text((x, y), title, fill='black', font=title_font)
        
        # Draw hook if exists
        if hook:
            # Word wrap hook text
            words = hook.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                bbox = draw.textbbox((0, 0), test_line, font=hook_font)
                if bbox[2] - bbox[0] > self.config.width - 200:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw hook lines
            y_offset = y + text_height + 100
            for line in lines[:3]:  # Max 3 lines
                bbox = draw.textbbox((0, 0), line, font=hook_font)
                line_width = bbox[2] - bbox[0]
                x_pos = (self.config.width - line_width) // 2
                draw.text((x_pos, y_offset), line, fill='black', font=hook_font)
                y_offset += 70
        
        # Save intro image
        intro_img_path = os.path.join(self.temp_dir, "intro.png")
        img.save(intro_img_path)
        
        # Create video from intro image
        intro_video_path = os.path.join(self.temp_dir, "intro.mp4")
        self._create_fade_animation(intro_img_path, intro_video_path, 3)
        
        return intro_video_path
    
    def _create_outro(self, script: Dict, citations: List[Dict]) -> str:
        """Create outro with citations"""
        
        img = Image.new('RGB', (self.config.width, self.config.height), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # "Thanks for watching"
        thanks_text = "Thanks for watching!"
        bbox = draw.textbbox((0, 0), thanks_text, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (self.config.width - text_width) // 2
        y = 300
        draw.text((x, y), thanks_text, fill='black', font=title_font)
        
        # Source citation
        if citations:
            citation = citations[0]
            source_text = f"Source: {citation.get('title', 'Unknown')}"
            
            bbox = draw.textbbox((0, 0), source_text, font=text_font)
            text_width = bbox[2] - bbox[0]
            x = (self.config.width - text_width) // 2
            y = 800
            draw.text((x, y), source_text, fill='gray', font=text_font)
            
            # Author if available
            if citation.get('author') and citation['author'] != 'Unknown':
                author_text = f"By {citation['author']}"
                bbox = draw.textbbox((0, 0), author_text, font=text_font)
                text_width = bbox[2] - bbox[0]
                x = (self.config.width - text_width) // 2
                y = 900
                draw.text((x, y), author_text, fill='gray', font=text_font)
        
        # Save outro image
        outro_img_path = os.path.join(self.temp_dir, "outro.png")
        img.save(outro_img_path)
        
        # Create video
        outro_video_path = os.path.join(self.temp_dir, "outro.mp4")
        self._create_simple_video(outro_img_path, outro_video_path, 3)
        
        return outro_video_path
    
    def _concatenate_videos(self, video_paths: List[str]) -> str:
        """Concatenate multiple videos into one"""
        
        # Create concat file for FFmpeg
        concat_file = os.path.join(self.temp_dir, "concat_list.txt")
        with open(concat_file, 'w') as f:
            for video_path in video_paths:
                if os.path.exists(video_path):
                    f.write(f"file '{os.path.abspath(video_path)}'\n")
        
        # Concatenate using FFmpeg
        output_path = os.path.join(self.temp_dir, "concatenated.mp4")
        subprocess.run([
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y', output_path
        ], check=True, capture_output=True)
        
        return output_path
    
    def _add_audio(self, video_path: str, audio_path: str, output_path: str) -> str:
        """Add audio track to video"""
        
        if not os.path.exists(audio_path):
            # No audio, just copy video
            subprocess.run(['cp', video_path, output_path], check=True)
            return output_path
        
        # Merge video and audio
        subprocess.run([
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',  # Match shortest duration
            '-y', output_path
        ], check=True, capture_output=True)
        
        return output_path