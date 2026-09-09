def normalize_fact(raw_fact, page_number, document_name):
    """Normalize raw LLM extracted fact into predictable dictionary structure."""
    confidence = raw_fact.get("confidence")
    if confidence is None:
        confidence = 0.95 if raw_fact.get("value") is not None else 0.5

    # Extract all extra fields dynamically into attributes
    known_keys = {"subject", "property", "evidence", "confidence"}
    attributes = {}
    for k, v in raw_fact.items():
        if k not in known_keys:
            attributes[k] = v

    normalized_fact = {
        "subject": raw_fact.get("subject") or "Unspecified Entity",
        "property": raw_fact.get("property") or "unspecified_property",
        "attributes": attributes,
        "evidence": {
            "text": raw_fact.get("evidence") or "",
            "page": page_number,
            "document": document_name
        },
        "confidence": confidence
    }

    return normalized_fact