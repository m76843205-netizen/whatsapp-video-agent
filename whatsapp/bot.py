import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from agent.core import AgentCore
from renderer.video_renderer import VideoRenderer

class WhatsAppBot:
    def __init__(self):
        self.agent = AgentCore()
        self.renderer = VideoRenderer()

    def handle(self, text):
        text = text.strip()
        if text.lower().startswith("render "):
            topic = text[7:].strip()
            if not topic:
                return "❌ Format: render <topic>"
            try:
                path = self.renderer.render_video(topic)
                return f"✅ Video ready!\n📁 {path}"
            except Exception as e:
                return f"❌ Error: {e}"
        return self.agent.ask(text)

if __name__ == "__main__":
    bot = WhatsAppBot()
    print("🤖 Agent ready! (quit = exit)")
    while True:
        try:
            msg = input("You: ").strip()
            if msg.lower() in ("quit","exit"): break
            if msg: print(f"\nAgent: {bot.handle(msg)}\n")
        except KeyboardInterrupt:
            break
