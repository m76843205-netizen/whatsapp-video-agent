import json
from agent.providers.groq import GroqProvider
from agent.tools.executor import ToolExecutor


class AgentCore:
    def __init__(self):
        self.brain = GroqProvider()
        self.executor = ToolExecutor()
        self.history = []

        self.system_prompt = """
You are an intelligent general-purpose AI project agent.

Understand natural language instructions.
Analyze projects, files, folders and documentation.
Plan tasks and select available tools when useful.
Never pretend a tool was executed if it was not.
Preserve user data and ask permission before destructive actions.
Use actual tool results when answering.
"""

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_project_files",
                    "description": "List files and folders recursively inside a project directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to inspect"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    }
                }
            },
            {'type': 'function', 'function': {'name': 'read_project_file', 'description': 'Read a supported project text or code file.', 'parameters': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path'], 'additionalProperties': False}}}
        ]

    def ask(self, message):
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(self.history[-10:])
        messages.append({"role": "user", "content": message})

        answer = ""

        for round_number in range(5):
            response = self.brain.chat(messages, tools=self.tools)
            messages.append(response)

            tool_calls = response.get("tool_calls")

            if not tool_calls:
                answer = response.get("content") or ""
                break

            for call in tool_calls:
                name = call["function"]["name"]
                raw_args = call["function"].get("arguments") or "{}"

                try:
                    arguments = json.loads(raw_args)
                    result = self.executor.execute(name, arguments)
                    output = json.dumps(result, ensure_ascii=False)
                except Exception as error:
                    output = json.dumps({"error": str(error)})

                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": output
                })

        else:
            answer = "Tool-calling limit reached. Please continue with a smaller task."

        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": answer})

        return answer
