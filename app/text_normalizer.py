import re

# Canonical property dictionary mapping common variations to unified keys
CANONICAL_PROPERTY_MAP = {
    # Revenue variants
    "revenue": "revenue",
    "annual revenue": "revenue",
    "total revenue": "revenue",
    "sales revenue": "revenue",
    "fy2024 revenue": "revenue",
    "fy2023 revenue": "revenue",
    
    # Employee variants
    "employees": "employee_count",
    "employee count": "employee_count",
    "number of employees": "employee_count",
    "workforce size": "employee_count",
    "total employees": "employee_count",
    "headcount": "employee_count",
    "staff count": "employee_count",

    # Profit variants
    "operating profit": "operating_profit",
    "operating income": "operating_profit",
    "ebit": "operating_profit",
    "net profit": "operating_profit",

    # Shipment variants
    "shipments": "shipment_volume",
    "shipment volume": "shipment_volume",
    "total shipments": "shipment_volume",
    "number of shipments": "shipment_volume",

    # Debt / Financial
    "debt": "debt",
    "total debt": "debt",
    "cash": "cash_reserves",
    "cash reserves": "cash_reserves",
    "cash and cash equivalents": "cash_reserves",

    # Operations
    "fulfillment centers": "fulfillment_centers",
    "number of fulfillment centers": "fulfillment_centers",
    "utilization": "utilization_rate",
    "utilization rate": "utilization_rate",
    "capacity utilization": "utilization_rate"
}


def normalize_property_name(property_name):
    """Clean lexical normalization of property string."""
    if not property_name:
        return ""

    property_name = property_name.lower()
    property_name = property_name.replace("_", " ")
    property_name = re.sub(r"[^a-z0-9\s-]", "", property_name)
    property_name = re.sub(r"\s+", " ", property_name)
    return property_name.strip()


def get_canonical_property(property_name):
    """Map normalized property to a canonical property key."""
    norm = normalize_property_name(property_name)
    if norm in CANONICAL_PROPERTY_MAP:
        return CANONICAL_PROPERTY_MAP[norm]
    
    # Check if any canonical key is a substring or key words match
    for key, canonical in CANONICAL_PROPERTY_MAP.items():
        if norm == key or norm.endswith(" " + key) or norm.startswith(key + " "):
            return canonical

    return norm


def are_properties_semantically_matching(prop1, prop2):
    """Determine whether two property names refer to the same conceptual property."""
    canon1 = get_canonical_property(prop1)
    canon2 = get_canonical_property(prop2)
    
    if canon1 and canon2 and canon1 == canon2:
        return True

    # Token set overlap check for unseen properties
    tokens1 = set(normalize_property_name(prop1).split())
    tokens2 = set(normalize_property_name(prop2).split())
    
    # Remove generic stopwords
    stopwords = {"of", "the", "in", "for", "total", "annual", "number"}
    tokens1 -= stopwords
    tokens2 -= stopwords

    if not tokens1 or not tokens2:
        return False

    intersection = tokens1.intersection(tokens2)
    min_len = min(len(tokens1), len(tokens2))
    
    # If key terms overlap significantly (e.g. employee / employees)
    if intersection and len(intersection) / min_len >= 0.5:
        return True

    return False