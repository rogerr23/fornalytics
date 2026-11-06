"""Text helpers shared by the extractors."""


def decode_text(data: bytes) -> str:
    """UTF-8 (with or without BOM), falling back to Latin-1 for old files. Newlines become \\n."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    return text.replace("\r\n", "\n").replace("\r", "\n")
