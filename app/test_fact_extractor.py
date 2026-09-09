from app.app.fact_extractor import extract_facts


text = """
Revenue for FY2024 was $100 million.

The company employed 5,000 people.
"""


facts = extract_facts(text)


for fact in facts:
    print("\nFACT")
    print("Subject:", fact["subject"])
    print("Property:", fact["property"])
    print("Value:", fact["value"])
    print("Unit:", fact["unit"])
    print("Period:", fact["period"])
    print("Evidence:", fact["evidence"])