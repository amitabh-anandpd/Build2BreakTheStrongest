from gtts import gTTS

class Narrator:
    def __init__(self, script, output_audio="voice.mp3"):
        self.script = script
        self.output_audio = output_audio

    def synthesize_audio(self):
        """Use gTTS for simplicity."""
        tts = gTTS(text=self.script, lang='en')
        tts.save(self.output_audio)
        return self.output_audio