import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.chunker import TextChunker


def test_chunker_splits_long_text():
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    pages = [{"page": 1, "text": "Python " * 30}]

    chunks = chunker.split_pages(pages, source_name="test")

    assert len(chunks) > 1
    assert chunks[0].chunk_id.startswith("test-p1-c")