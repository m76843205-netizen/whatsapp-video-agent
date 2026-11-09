import agent.readers.stream_reader as reader

reader.MAX_CHUNK_SIZE = 8
parts = []

result = reader.read_entire_text_file(
    "test_data.txt", parts.append
)

original = open("test_data.txt", encoding="utf-8").read()
reconstructed = "".join(parts)

print("RESULT:", result)
print("EXACT MATCH:", original == reconstructed)
print("CHUNKS:", len(parts))
