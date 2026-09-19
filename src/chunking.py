from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunks.append(" ".join(sentences[i : i + self.max_sentences_per_chunk]))
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            chunks = []
            for i in range(0, len(current_text), self.chunk_size):
                chunks.append(current_text[i : i + self.chunk_size])
            return chunks

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        if sep == "":
            chunks = []
            for i in range(0, len(current_text), self.chunk_size):
                chunks.append(current_text[i : i + self.chunk_size])
            return chunks

        parts = current_text.split(sep)
        
        processed_parts = []
        for part in parts:
            if len(part) > self.chunk_size:
                processed_parts.extend(self._split(part, next_seps))
            else:
                processed_parts.append(part)
                
        merged = []
        current_chunk = ""
        
        for part in processed_parts:
            if not current_chunk:
                current_chunk = part
            else:
                if len(current_chunk) + len(sep) + len(part) <= self.chunk_size:
                    current_chunk += sep + part
                else:
                    merged.append(current_chunk)
                    current_chunk = part
        if current_chunk:
            merged.append(current_chunk)
            
        return merged


class HeadingChunker:
    HEADING = re.compile(r"^(#{2,6}\s+\S.*|Điều\s+\d+.*)$", re.MULTILINE)

    def __init__(self, chunk_size: int = 500, drop_notes: bool = True) -> None:
        self.chunk_size = chunk_size
        self.drop_notes = drop_notes

    def chunk(self, text: str) -> list[str]:
        starts = [m.start() for m in self.HEADING.finditer(text)]
        if not starts:
            return RecursiveChunker(chunk_size=self.chunk_size).chunk(text)

        preamble = text[: starts[0]].strip()
        if self.drop_notes:
            preamble = "\n".join(line for line in preamble.splitlines() if not line.startswith(">")).strip()
        chunks: list[str] = []
        for begin, end in zip(starts, starts[1:] + [len(text)]):
            section = text[begin:end].strip()
            if section:
                chunks.extend(self._split_section(section))
        if preamble:
            if chunks:
                chunks[0] = f"{preamble}\n\n{chunks[0]}"
            else:
                chunks.append(preamble)
        return chunks

    def _split_section(self, section: str) -> list[str]:
        if len(section) <= self.chunk_size:
            return [section]
        heading, _, body = section.partition("\n")
        inner_size = max(self.chunk_size - len(heading) - 1, 100)
        return [f"{heading}\n{piece}" for piece in RecursiveChunker(chunk_size=inner_size).chunk(body)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = sum(x*x for x in vec_a) ** 0.5
    norm_b = sum(x*x for x in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if not text:
            return {
                "fixed_size": {"count": 0, "avg_length": 0.0, "chunks": []},
                "by_sentences": {"count": 0, "avg_length": 0.0, "chunks": []},
                "recursive": {"count": 0, "avg_length": 0.0, "chunks": []}
            }
        
        fs = FixedSizeChunker(chunk_size=chunk_size)
        bs = SentenceChunker(max_sentences_per_chunk=3)
        rc = RecursiveChunker(chunk_size=chunk_size)
        
        c_fs = fs.chunk(text)
        c_bs = bs.chunk(text)
        c_rc = rc.chunk(text)
        
        def stats(chunks):
            if not chunks: return {"count": 0, "avg_length": 0.0, "chunks": []}
            return {
                "count": len(chunks),
                "avg_length": sum(len(c) for c in chunks) / len(chunks),
                "chunks": chunks
            }
            
        return {
            "fixed_size": stats(c_fs),
            "by_sentences": stats(c_bs),
            "recursive": stats(c_rc)
        }
