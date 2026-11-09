import json
from agent.providers.groq import GroqProvider

class ScriptGenerator:
    def __init__(self):
        self.brain = GroqProvider()

    def generate(self, topic, skill_meta):
        messages = [
            {"role": "system", "content": "You are a video script generator. Return ONLY valid JSON, no explanation."},
            {"role": "user", "content": f"""
Topic: {topic}
Skill: {json.dumps(skill_meta)}

Return JSON:
{{
  "title": "video title",
  "duration": 30,
  "scenes": [
    {{"id": 1, "type": "title", "text": "main title", "subtext": "subtitle", "duration": 3}},
    {{"id": 2, "type": "content", "heading": "heading", "points": ["p1","p2","p3"], "duration": 10}},
    {{"id": 3, "type": "code", "heading": "Example", "code": "print('hello')", "duration": 10}},
    {{"id": 4, "type": "outro", "text": "Thanks!", "duration": 5}}
  ]
}}
"""}
        ]
        response = self.brain.generate(messages)
        clean = response.replace("```json","").replace("```","").strip()
        return json.loads(clean)
