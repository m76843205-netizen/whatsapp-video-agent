import os
import subprocess

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "videos")

class FFmpegRenderer:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def render(self, script, output_name="output"):
        frames_dir = os.path.join(OUTPUT_DIR, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        frame_number = 0
        fps = 30

        for scene in script.get("scenes", []):
            duration = scene.get("duration", 3)
            total_frames = duration * fps
            for _ in range(total_frames):
                frame_path = os.path.join(frames_dir, f"frame_{frame_number:05d}.png")
                self._create_frame(scene, frame_path)
                frame_number += 1

        output_path = os.path.join(OUTPUT_DIR, f"{output_name}.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(frames_dir, "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")

        for f in os.listdir(frames_dir):
            os.remove(os.path.join(frames_dir, f))
        os.rmdir(frames_dir)

        return output_path

    def _create_frame(self, scene, output_path):
        scene_type = scene.get("type", "title")
        colors = {
            "title": ("0x1a1a2e", "0xffffff"),
            "content": ("0x16213e", "0xffffff"),
            "code": ("0x0f3460", "0x00ff88"),
            "outro": ("0x1a1a2e", "0xe94560"),
        }
        bg, fg = colors.get(scene_type, ("0x1a1a2e", "0xffffff"))

        if scene_type == "title":
            text = scene.get("text", "")
        elif scene_type == "content":
            points = scene.get("points", [])
            text = scene.get("heading","") + " | " + " | ".join(points)
        elif scene_type == "code":
            text = scene.get("heading","") + ": " + scene.get("code","")
        else:
            text = scene.get("text", "")

        safe = text.replace("'", "").replace(":", " ").replace("\\n", " ")[:80]

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={bg}:size=1280x720:rate=1",
            "-vframes", "1",
            "-vf", f"drawtext=text='{safe}':fontcolor={fg}:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2",
            output_path
        ]
        subprocess.run(cmd, capture_output=True)
