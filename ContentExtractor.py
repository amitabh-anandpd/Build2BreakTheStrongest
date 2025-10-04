import fitz
from GeminiLLM import GeminiLLM

class ContentExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_text(self):
        """Extract raw text from PDF."""
        doc = fitz.open(self.pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def summarize(self, text):
        """Summarize PDF content into 20s explainer format."""
        model = GeminiLLM()
        prompt = f"""
        Summarize this PDF text into a short, engaging script outline suitable for a 20-second YouTube short.
        Include:
        - Hook (1 line)
        - Body (2-3 sentences)
        - Outro (1 line)
        - Visual suggestions (in bullet points)
        - Citation text (based on context)
        
        Text:
        {text[:8000]}  # limit to keep under token cap
        """
        response = model.generate_content(prompt)
        return response.text

    def run(self):
        pdf_text = self.extract_text()
        summary = self.summarize(pdf_text)
        return summary