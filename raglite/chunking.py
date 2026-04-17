"""Chunking sentence-aware per il laboratorio."""

from __future__ import annotations


def _split_sentences(text: str) -> list[str]:
    """Divide il testo in frasi senza spezzarle a metà."""
    text = text.strip()
    if not text:
        return []

    sentences: list[str] = []
    current: list[str] = []

    for char in text:
        current.append(char)
        if char in ".!?":
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []

    tail = "".join(current).strip()
    if tail:
        sentences.append(tail)

    return sentences

def chunk_text(text: str, size: int, overlap: int) -> list[tuple[int, str]]:
    """Restituisce chunk testuali con overlap in numero di frasi."""
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks: list[tuple[int, str]] = []
    chunk_id = 0
    i = 0

    while i < len(sentences):
        acc: list[str] = []
        char_count = 0
        j = i

        # Aggiungi frasi intere finché il chunk resta entro size.
        # Poi salva (chunk_id, testo_chunk) e avanza lasciando overlap frasi in comune.

        while j < len(sentences) and char_count < size:
            s = sentences[j]
            if char_count + len(s)<= size:
                acc.append(s)
                char_count += len(s)
                j += 1
            else:
                break
        chunks.append((chunk_id, " ".join(acc)))  
        chunk_id += 1
        i += max(1, len(acc) - overlap)
    return chunks