from GeminiLLM import GeminiLLM

class ScriptWriter:
    def __init__(self, summary):
        self.summary = summary

    def write_script(self):
        """Generate final 20-second script from summary."""
        model = GeminiLLM()
        prompt = f"""
        Create a conversational, engaging 20-second voiceover script for a YouTube short
        based on this summary. Use natural language and storytelling tone.
        Keep total duration ≈ 50 words (20s).

        Summary:
        {self.summary}
        """
        response = model.generate_content(prompt)
        return response.text