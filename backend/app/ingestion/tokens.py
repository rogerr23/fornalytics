"""Token estimate without calling any API (characters / 4)."""

import math

CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / CHARS_PER_TOKEN)
