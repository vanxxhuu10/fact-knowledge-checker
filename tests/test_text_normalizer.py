import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("app"))

from text_normalizer import normalize_property_name, get_canonical_property, are_properties_semantically_matching


def test_normalize_property_name():
    assert normalize_property_name("customer_retention_rate") == "customer retention rate"
    assert normalize_property_name("Customer Retention Rate!") == "customer retention rate"
    assert normalize_property_name("  headcount   ") == "headcount"


def test_canonical_property_mapping():
    assert get_canonical_property("employee count") == "employee_count"
    assert get_canonical_property("number of employees") == "employee_count"
    assert get_canonical_property("workforce size") == "employee_count"
    assert get_canonical_property("total revenue") == "revenue"
    assert get_canonical_property("operating profit") == "operating_profit"


def test_are_properties_semantically_matching():
    assert are_properties_semantically_matching("employee_count", "number of employees") is True
    assert are_properties_semantically_matching("annual revenue", "revenue") is True
    assert are_properties_semantically_matching("revenue", "workforce size") is False
