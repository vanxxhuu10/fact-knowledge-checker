import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("app"))

from fact_normalizer import normalize_fact


def test_normalize_fact_structure():
    raw = {
        "subject": "Northstar Logistics",
        "property": "revenue",
        "value": 120,
        "unit": "million",
        "period": "FY2024",
        "evidence": "Revenue was $120 million in FY2024.",
        "confidence": 0.95
    }

    norm = normalize_fact(raw, page_number=2, document_name="test.pdf")
    assert norm["subject"] == "Northstar Logistics"
    assert norm["property"] == "revenue"
    assert norm["attributes"]["value"] == 120
    assert norm["attributes"]["unit"] == "million"
    assert norm["attributes"]["period"] == "FY2024"
    assert norm["evidence"]["text"] == "Revenue was $120 million in FY2024."
    assert norm["evidence"]["page"] == 2
    assert norm["evidence"]["document"] == "test.pdf"
    assert norm["confidence"] == 0.95


def test_normalize_fact_missing_fields():
    raw = {
        "subject": None,
        "property": None,
        "value": None,
        "evidence": None
    }
    norm = normalize_fact(raw, page_number=1, document_name="unknown.pdf")
    assert norm["subject"] == "Unspecified Entity"
    assert norm["property"] == "unspecified_property"
    assert norm["confidence"] == 0.5
