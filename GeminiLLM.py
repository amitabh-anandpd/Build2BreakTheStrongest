import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

class GeminiLLM:
    """
    Gemini Flash 2.0 integration for reasoning and response generation.
    Handles the 'thinking' part of the ReAct pattern.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_response(self, prompt: str) -> str:
        """
        Generate response using Gemini model.

        Args:
            prompt (str): Input prompt for the model

        Returns:
            str: Generated response
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"