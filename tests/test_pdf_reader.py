import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("app"))

from pdf_reader import extract_text_from_pdf, calculate_file_hash


def test_calculate_file_hash_bytes():
    data = b"Sample PDF binary stream content"
    h1 = calculate_file_hash(data)
    h2 = calculate_file_hash(data)
    assert h1 == h2
    assert len(h1) == 64 # SHA-256 hex string length


def test_pdf_extraction_sample():
    demo_pdf = os.path.abspath(r"data/demo/case1_corroboration_docA.pdf")
    if os.path.exists(demo_pdf):
        pages = extract_text_from_pdf(demo_pdf)
        assert isinstance(pages, list)
        assert len(pages) >= 1
        assert "page_number" in pages[0]
        assert pages[0]["page_number"] == 1
        assert "text" in pages[0]
        assert "Northstar" in pages[0]["text"]
