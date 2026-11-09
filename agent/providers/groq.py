import os
import json
import urllib.request
import urllib.error


class GroqProvider:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing")

        if not self.model:
            raise ValueError("GROQ_MODEL is missing")

    def chat(self, messages, tools=None):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.4
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            self.API_URL,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "curl/8.14.1"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))

            return result["choices"][0]["message"]

        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Groq API Error {error.code}: {details}"
            ) from error

        except urllib.error.URLError as error:
            raise RuntimeError(
                f"Network Error: {error.reason}"
            ) from error

    def generate(self, messages):
        message = self.chat(messages)
        return message.get("content") or ""
