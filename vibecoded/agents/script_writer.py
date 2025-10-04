"""
agents/script_writer.py
Generates video scripts using Gemini API
"""

import google.generativeai as genai
from typing import Dict, List
import json
import time


class ScriptWriter:
    """Generates YouTube Shorts scripts using Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-2.0-flash-exp'):
        """
        Initialize ScriptWriter with Gemini API
        
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        genai.configure(api_key=api_key)
        # Try to use the specified model, fallback to alternatives if not available
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            print(e)
            fallback_models = [
                'gemini-2.0-flash-exp',
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash-002',
                'gemini-1.5-flash',
                'gemini-pro'
            ]
            for fallback in fallback_models:
                try:
                    self.model = genai.GenerativeModel(fallback)
                    print(f"Using model: {fallback}")
                    break
                except Exception:
                    continue
        
    def generate_script(self, content_data: Dict, max_duration: int = 60) -> Dict:
        """
        Generate a video script from extracted content
        
        Args:
            content_data: Dictionary with text, metadata, sections
            max_duration: Maximum video duration in seconds
            
        Returns:
            Dictionary containing script with scenes
        """
        # Prepare prompt for Gemini
        prompt = self._create_prompt(content_data, max_duration)
        
        # Generate script with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                script_text = response.text
                
                # Parse the response into structured format
                script = self._parse_script(script_text, content_data)
                
                return script
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    raise
    
    def _create_prompt(self, content_data: Dict, max_duration: int) -> str:
        """Create detailed prompt for Gemini"""
        
        text = content_data['text'][:4000]  # Limit input length
        title = content_data['metadata'].get('title', 'Untitled')
        
        prompt = f"""You are a creative scriptwriter for YouTube Shorts. Transform this PDF content into an engaging {max_duration}-second video script.

SOURCE DOCUMENT:
Title: {title}
Content: {text}

REQUIREMENTS:
1. Create a script for a {max_duration}-second YouTube Short (approximately {max_duration * 2.5} words)
2. Focus on the MOST interesting/surprising/valuable insight from the content
3. Write in a conversational, engaging tone (not academic)
4. Structure with 5-7 scenes, each 8-12 seconds long
5. For each scene, specify:
   - Narration (what to say)
   - Visual description (what doodle/sketch to show)
   - Duration in seconds
   - Key visual elements

OUTPUT FORMAT (respond with valid JSON):
{{
  "hook": "Opening line that grabs attention",
  "title": "Catchy video title",
  "scenes": [
    {{
      "scene_number": 1,
      "duration": 8,
      "narration": "Engaging narration text",
      "visual_description": "Describe the doodle/sketch to draw",
      "visual_elements": ["element1", "element2", "element3"],
      "animation_type": "draw_on|fade_in|morph|zoom"
    }}
  ],
  "conclusion": "Final takeaway or call-to-action",
  "source_title": "{title}"
}}

VISUAL STYLE GUIDELINES:
- Doodles should be simple, hand-drawn style illustrations
- Use metaphors and visual analogies
- Minimize text overlays (use visuals to tell the story)
- Think: RSA Animate, Kurzgesagt, or whiteboard animation style

Focus on making it VISUAL and ENGAGING. No boring slides with bullet points!"""

        return prompt
    
    def _parse_script(self, script_text: str, content_data: Dict) -> Dict:
        """Parse Gemini's response into structured script"""
        
        try:
            # Try to extract JSON from the response
            json_start = script_text.find('{')
            json_end = script_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = script_text[json_start:json_end]
                script = json.loads(json_str)
            else:
                # Fallback: create structured script from text
                script = self._fallback_parse(script_text)
            
            # Ensure required fields
            if 'scenes' not in script:
                script['scenes'] = []
            
            # Add metadata
            script['source_metadata'] = content_data['metadata']
            script['citations'] = content_data.get('citations', [])
            
            # Validate and adjust scene durations
            total_duration = sum(scene.get('duration', 10) for scene in script['scenes'])
            if total_duration > 60:
                # Scale down durations proportionally
                scale = 55 / total_duration  # Leave 5 seconds for intro/outro
                for scene in script['scenes']:
                    scene['duration'] = int(scene.get('duration', 10) * scale)
            
            return script
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return self._fallback_parse(script_text)
    
    def _fallback_parse(self, script_text: str) -> Dict:
        """Create a basic script structure if JSON parsing fails"""
        
        lines = script_text.split('\n')
        narration_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
        
        # Split into scenes (roughly 10 seconds each)
        words_per_scene = 25  # ~2.5 words per second * 10 seconds
        scenes = []
        
        for i in range(0, len(narration_lines), 2):
            scene_text = ' '.join(narration_lines[i:i+2])
            if len(scene_text.split()) > words_per_scene:
                scene_text = ' '.join(scene_text.split()[:words_per_scene])
            
            scenes.append({
                'scene_number': len(scenes) + 1,
                'duration': 10,
                'narration': scene_text,
                'visual_description': 'Simple doodle illustration',
                'visual_elements': ['sketch', 'drawing'],
                'animation_type': 'draw_on'
            })
        
        return {
            'hook': narration_lines[0] if narration_lines else 'Interesting content ahead!',
            'title': 'Video from PDF',
            'scenes': scenes[:6],  # Max 6 scenes for 60 seconds
            'conclusion': 'Thanks for watching!',
            'source_title': 'PDF Document'
        }