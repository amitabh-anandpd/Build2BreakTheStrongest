"""
agents/visuals_maker.py
Generates doodle-style visuals using Stable Diffusion and image processing
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from typing import Dict, List, Tuple
import random
import requests
import io


class VisualsMaker:
    """Creates doodle-style visuals for video scenes"""
    
    def __init__(self, style: str = "doodle"):
        """
        Initialize VisualsMaker
        
        Args:
            style: Visual style - 'doodle', 'whiteboard', or 'sketch'
        """
        self.style = style
        self.width = 1080
        self.height = 1920
        self.output_dir = "temp_processing/visuals"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Style presets
        self.style_prompts = {
            'doodle': 'simple line art doodle, hand-drawn sketch, minimalist illustration, black and white, clean lines',
            'whiteboard': 'whiteboard marker drawing, dry erase style, hand-drawn diagram, educational illustration',
            'sketch': 'pencil sketch, hand-drawn illustration, artistic drawing, sketch style'
        }
    
    def generate_visuals(self, script: Dict) -> Dict:
        """
        Generate visual assets for each scene in the script
        
        Args:
            script: Script dictionary with scenes
            
        Returns:
            Dictionary mapping scene numbers to visual asset paths
        """
        visual_assets = {}
        
        scenes = script.get('scenes', [])
        print(f"Generating visuals for {len(scenes)} scenes...")
        
        for scene in scenes:
            scene_num = scene.get('scene_number', 0)
            print(f"  - Scene {scene_num}...")
            
            # Generate visual for this scene
            visual_path = self._generate_scene_visual(scene, scene_num)
            
            visual_assets[scene_num] = {
                'path': visual_path,
                'duration': scene.get('duration', 10),
                'animation_type': scene.get('animation_type', 'draw_on')
            }
        
        return visual_assets
    
    def _generate_scene_visual(self, scene: Dict, scene_num: int) -> str:
        """Generate visual for a single scene"""
        
        visual_desc = scene.get('visual_description', '')
        visual_elements = scene.get('visual_elements', [])
        
        # Create canvas
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Method 1: Use local generation (fast, always works)
        self._draw_doodle_style(draw, visual_desc, visual_elements)
        
        # Method 2: Alternative - call Stable Diffusion API if available
        # Uncomment and configure if you have SD API access:
        # img = self._generate_with_stable_diffusion(visual_desc)
        
        # Add sketch/doodle effects
        img = self._apply_style_effects(img)
        
        # Save
        output_path = os.path.join(self.output_dir, f"scene_{scene_num:02d}.png")
        img.save(output_path, quality=95)
        
        return output_path
    
    def _draw_doodle_style(self, draw: ImageDraw.Draw, description: str, elements: List[str]):
        """Draw simple doodle-style illustrations directly"""
        
        # Background - subtle texture
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point((x, y), fill=(240, 240, 240))
        
        # Draw elements based on keywords
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Common visual elements
        if any(word in description.lower() for word in ['circle', 'round', 'cycle']):
            self._draw_wobbly_circle(draw, center_x, center_y, 300)
        
        if any(word in description.lower() for word in ['arrow', 'direction', 'flow']):
            self._draw_hand_drawn_arrow(draw, center_x - 200, center_y, center_x + 200, center_y)
        
        if any(word in description.lower() for word in ['person', 'human', 'people']):
            self._draw_stick_figure(draw, center_x, center_y + 200)
        
        if any(word in description.lower() for word in ['brain', 'mind', 'thinking']):
            self._draw_brain_doodle(draw, center_x, center_y - 200)
        
        if any(word in description.lower() for word in ['star', 'spark', 'shine']):
            for _ in range(5):
                x = random.randint(100, self.width - 100)
                y = random.randint(100, self.height - 100)
                self._draw_star(draw, x, y, 40)
        
        # Draw text labels for key elements
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        except:
            font = ImageFont.load_default()
        
        for i, element in enumerate(elements[:3]):
            y_pos = 200 + (i * 150)
            # Hand-written style text
            self._draw_sketchy_text(draw, element, center_x, y_pos, font)
    
    def _draw_wobbly_circle(self, draw: ImageDraw.Draw, cx: int, cy: int, radius: int):
        """Draw a hand-drawn style circle"""
        points = []
        for angle in range(0, 360, 5):
            rad = np.radians(angle)
            wobble = random.randint(-10, 10)
            r = radius + wobble
            x = cx + r * np.cos(rad)
            y = cy + r * np.sin(rad)
            points.append((x, y))
        
        # Draw with multiple overlapping lines for sketchy effect
        for _ in range(3):
            offset_points = [(x + random.randint(-2, 2), y + random.randint(-2, 2)) for x, y in points]
            draw.line(offset_points + [offset_points[0]], fill='black', width=3)
    
    def _draw_hand_drawn_arrow(self, draw: ImageDraw.Draw, x1: int, y1: int, x2: int, y2: int):
        """Draw a sketchy arrow"""
        # Main line with wobble
        segments = 20
        points = []
        for i in range(segments + 1):
            t = i / segments
            x = x1 + (x2 - x1) * t + random.randint(-5, 5)
            y = y1 + (y2 - y1) * t + random.randint(-5, 5)
            points.append((x, y))
        
        draw.line(points, fill='black', width=4)
        
        # Arrowhead
        angle = np.arctan2(y2 - y1, x2 - x1)
        arrow_len = 40
        angle1 = angle + np.radians(150)
        angle2 = angle - np.radians(150)
        
        p1 = (x2 + arrow_len * np.cos(angle1), y2 + arrow_len * np.sin(angle1))
        p2 = (x2 + arrow_len * np.cos(angle2), y2 + arrow_len * np.sin(angle2))
        
        draw.line([p1, (x2, y2), p2], fill='black', width=4)
    
    def _draw_stick_figure(self, draw: ImageDraw.Draw, cx: int, cy: int):
        """Draw a simple stick figure"""
        # Head
        self._draw_wobbly_circle(draw, cx, cy - 100, 60)
        # Body
        draw.line([(cx, cy - 40), (cx, cy + 80)], fill='black', width=4)
        # Arms
        draw.line([(cx - 60, cy), (cx + 60, cy)], fill='black', width=4)
        # Legs
        draw.line([(cx, cy + 80), (cx - 40, cy + 160)], fill='black', width=4)
        draw.line([(cx, cy + 80), (cx + 40, cy + 160)], fill='black', width=4)
    
    def _draw_brain_doodle(self, draw: ImageDraw.Draw, cx: int, cy: int):
        """Draw a simplified brain doodle"""
        # Simplified brain outline with curves
        points = []
        for angle in range(0, 180, 10):
            rad = np.radians(angle)
            r = 150 + 30 * np.sin(rad * 3)
            x = cx + r * np.cos(rad)
            y = cy + r * np.sin(rad)
            points.append((x, y))
        
        draw.line(points, fill='black', width=4)
        
        # Add squiggles inside
        for i in range(5):
            start_x = cx - 100 + i * 40
            y = cy - 50
            squiggle = [(start_x + j * 10, y + 20 * np.sin(j * 0.5)) for j in range(10)]
            draw.line(squiggle, fill='black', width=3)
    
    def _draw_star(self, draw: ImageDraw.Draw, cx: int, cy: int, size: int):
        """Draw a hand-drawn star"""
        points = []
        for i in range(10):
            angle = np.radians(i * 36)
            r = size if i % 2 == 0 else size // 2
            x = cx + r * np.cos(angle - np.pi / 2)
            y = cy + r * np.sin(angle - np.pi / 2)
            points.append((x, y))
        
        draw.polygon(points, outline='black', fill=None, width=3)
    
    def _draw_sketchy_text(self, draw: ImageDraw.Draw, text: str, x: int, y: int, font):
        """Draw text with sketchy effect"""
        # Draw text multiple times with slight offset for hand-drawn look
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            draw.text((x + dx, y + dy), text, fill=(200, 200, 200), font=font, anchor="mm")
        draw.text((x, y), text, fill='black', font=font, anchor="mm")
    
    def _apply_style_effects(self, img: Image.Image) -> Image.Image:
        """Apply style-specific effects to the image"""
        
        if self.style == 'sketch':
            # Add pencil texture
            img = img.filter(ImageFilter.CONTOUR)
            img = img.filter(ImageFilter.SMOOTH)
        
        elif self.style == 'whiteboard':
            # Slightly blur for marker effect
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Add slight noise for hand-drawn feel
        arr = np.array(img)
        noise = np.random.randint(-10, 10, arr.shape, dtype=np.int16)
        arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
        
        return img
    
    def _generate_with_stable_diffusion(self, description: str) -> Image.Image:
        """
        Generate image using Stable Diffusion API (optional enhancement)
        Configure with your SD API endpoint
        """
        # Example with Stable Diffusion API
        # You would need to set up your own SD instance or use a service
        
        full_prompt = f"{self.style_prompts[self.style]}, {description}, vertical format 9:16"
        
        # Placeholder - implement your SD API call here
        # api_url = "http://localhost:7860/sdapi/v1/txt2img"
        # payload = {
        #     "prompt": full_prompt,
        #     "negative_prompt": "color, photograph, realistic, complex, cluttered",
        #     "width": self.width,
        #     "height": self.height,
        #     "steps": 20,
        #     "cfg_scale": 7
        # }
        # response = requests.post(api_url, json=payload)
        # img_data = response.json()['images'][0]
        # img = Image.open(io.BytesIO(base64.b64decode(img_data)))
        
        # Fallback: return empty canvas
        return Image.new('RGB', (self.width, self.height), color='white')