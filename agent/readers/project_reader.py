import os

SUPPORTED = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".json", ".md", ".txt", ".yaml", ".yml",
    ".toml", ".html", ".css", ".xml",
    ".sh", ".ini", ".cfg", ".sql"
}

BLOCKED = {
    ".env", ".pem", ".key", ".p12", ".pfx"
}

MAX_SIZE = 100 * 1024


def read_project_file(path, start_line=1, max_lines=200):
    root = os.path.realpath(".")
    target = os.path.realpath(path)

    if os.path.commonpath([root, target]) != root:
        raise ValueError("Access outside project directory denied")

    if not os.path.isfile(target):
        raise ValueError("The requested path is not a file")

    name = os.path.basename(target).lower()
    extension = os.path.splitext(name)[1]

    if name in BLOCKED or extension in BLOCKED or name.startswith(".env"):
        raise ValueError("Reading sensitive files is not allowed")

    if (type(start_line) is not int or type(max_lines) is not int
            or start_line < 1 or max_lines < 1):
        raise ValueError("Invalid reading range")

    max_lines = min(max_lines, 500)
    selected = []

    try:
        with open(target, "r", encoding="utf-8") as file:
            for number, line in enumerate(file, 1):
                if number >= start_line:
                    if len(selected) >= max_lines:
                        break
                    selected.append(line)
    except UnicodeDecodeError:
        raise ValueError("File is not valid UTF-8 text")

    content = "".join(selected)
    has_more = len(selected) == max_lines and number >= start_line + max_lines

    return {
        "file": os.path.relpath(target, root),
        "characters": len(content),
        "start_line": start_line,
        "lines_read": len(selected),
        "has_more": has_more,
        "next_start_line": start_line + len(selected),
        "content": content
    }
