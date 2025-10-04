from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip

class Composer:
    def __init__(self, video_path, audio_path, citation, output_path="final.mp4"):
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path
        self.citation = citation

    def merge(self):
        video = VideoFileClip(self.video_path)
        audio = AudioFileClip(self.audio_path)
        video = video.set_audio(audio)

        txt = TextClip(self.citation, fontsize=30, color='black') \
            .set_duration(video.duration) \
            .set_position(("center", "bottom"))
        final = CompositeVideoClip([video, txt])
        final.write_videofile(self.output_path, fps=24)
        return self.output_path