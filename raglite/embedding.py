from __future__ import annotations

from array import array


def embed_text(text: str) -> list[float]:
    """Restituisce un embedding deterministico 4D."""
    b = text.encode("utf8")
    if not b:
        return [0.0, 0.0, 0.0, 0.0]
    return [
        float(len(b)),
        float(sum(b)),
        float(b[0]),
        float(b[-1]),
    ]


def vector_to_blob(vector: list[float]) -> bytes:
    """Serializza il vettore come BLOB SQLite."""
    return array("f", vector).tobytes()