from ContentExtractor import ContentExtractor
from ScriptWriter import ScriptWriter
from VisualMaker import VisualsMaker
from Narrator import Narrator
from Composer import Composer
from GeminiLLM import GeminiLLM

class PDFToShortPipeline:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def run(self):
        print("📄 Extracting and summarizing...")
        extractor = ContentExtractor(self.pdf_path)
        summary = extractor.run()

        print("✍️ Writing script...")
        writer = ScriptWriter(summary)
        script = writer.write_script()
        print(f"📝 Script:\n{script}\n")

        print("🎨 Generating visuals...")
        visuals = VisualsMaker(script)
        video_path = visuals.generate_video()

        print("🎙️ Generating voiceover...")
        narrator = Narrator(script)
        audio_path = narrator.synthesize_audio()

        print("🎬 Composing final video...")
        citation = "Source: " + "Extracted from PDF"
        composer = Composer(video_path, audio_path, citation)
        final_video = composer.merge()

        print(f"✅ Done! Final video: {final_video}")
        return final_video