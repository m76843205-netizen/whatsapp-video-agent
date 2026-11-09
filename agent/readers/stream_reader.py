import os

MAX_FILE_SIZE = 10 * 1024**3
MAX_CHUNK_SIZE = 1024 * 1024

BLOCKED = {".env", ".pem", ".key", ".p12", ".pfx"}


def validate_file(path):
    root = os.path.realpath(".")
    target = os.path.realpath(path)

    try:
        if os.path.commonpath([root, target]) != root:
            raise ValueError("Access outside project denied")
    except ValueError:
        raise ValueError("Invalid project path")

    if not os.path.isfile(target):
        raise ValueError("File not found")

    name = os.path.basename(target).lower()
    extension = os.path.splitext(name)[1]

    if name.startswith(".env") or extension in BLOCKED:
        raise ValueError("Sensitive file access denied")

    size = os.path.getsize(target)

    if size > MAX_FILE_SIZE:
        raise ValueError("File exceeds 10 GB limit")

    return target, size


def read_entire_text_file(path, process_chunk):
    target, size = validate_file(path)

    processed = 0
    chunk_size = MAX_CHUNK_SIZE
    pending = b""

    with open(target, "rb") as file:
        while True:
            raw = file.read(chunk_size)

            if not raw:
                break

            if b"\x00" in raw:
                raise ValueError("Binary file detected")

            data = pending + raw

            try:
                content = data.decode("utf-8")
                pending = b""
            except UnicodeDecodeError as error:
                if error.reason != "unexpected end of data":
                    raise ValueError("Invalid UTF-8 text")

                content = data[:error.start].decode("utf-8")
                pending = data[error.start:]

            if content:
                process_chunk(content)
                processed += len(content.encode("utf-8"))

    if pending:
        raise ValueError("Incomplete UTF-8 data at end of file")

    return {
        "file": os.path.relpath(target, os.path.realpath(".")),
        "size_bytes": size,
        "processed_bytes": processed,
        "complete": processed == size
    }
