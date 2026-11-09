from renderer.script_generator import ScriptGenerator
from renderer.ffmpeg_renderer import FFmpegRenderer

class VideoRenderer:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.ffmpeg = FFmpegRenderer()

    def render_video(self, topic, skill_meta=None, output_name=None):
        skill_meta = skill_meta or {}
        output_name = output_name or topic.replace(" ", "_")[:30]
        print(f"📝 Script generate ho raha hai: {topic}")
        script = self.script_gen.generate(topic, skill_meta)
        print(f"✅ {len(script.get('scenes', []))} scenes ready")
        print(f"🎬 Rendering...")
        path = self.ffmpeg.render(script, output_name)
        print(f"✅ Video ready: {path}")
        return path
