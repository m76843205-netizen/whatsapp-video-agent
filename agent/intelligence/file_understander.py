from agent.readers.stream_reader import read_entire_text_file
from agent.intelligence.knowledge_store import (
    create_document,
    save_chunk,
    finish_document
)
from agent.providers.groq import GroqProvider


class FileUnderstandingEngine:
    def __init__(self):
        self.brain = GroqProvider()


    def analyze_chunk(self, content):
        messages = [
            {
                "role": "system",
                "content": (
                    "Analyze the complete supplied text carefully. "
                    "Preserve facts, names, numbers, relationships, "
                    "instructions, and technical details. "
                    "Do not invent missing information. "
                    "Write a concise but detailed analysis."
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]

        result = self.brain.generate(messages)

        if not result:
            raise RuntimeError("Groq returned an empty analysis")

        return result

