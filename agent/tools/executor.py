from agent.tools.registry import TOOLS


class ToolExecutor:
    def execute(self, tool_name, arguments=None):
        arguments = arguments or {}

        tool = TOOLS.get(tool_name)

        if tool is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")

        return tool(**arguments)
