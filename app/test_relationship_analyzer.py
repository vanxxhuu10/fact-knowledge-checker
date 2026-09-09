from relationship_analyzer import analyze_relationship


fact1 = {
    "subject": "Northstar Logistics",
    "property": "number of employees",
    "attributes": {
        "value": 4800,
        "unit": None,
        "period": "FY2024"
    },
    "evidence": {
        "text": "The company employed 4,800 people in FY2024.",
        "page": 2,
        "document": "test1.pdf"
    }
}

fact2 = {
    "subject": "Northstar Logistics Limited",
    "property": "number_of_employees",
    "attributes": {
        "value": 6200,
        "unit": None,
        "period": "FY2024"
    },
    "evidence": {
        "text": "The company employed 6,200 people in FY2024.",
        "page": 3,
        "document": "test2.pdf"
    }
}


result = analyze_relationship(fact1, fact2)

print("Relationship:", result["relationship_type"])
print("Explanation:", result["explanation"])
print("Confidence:", result["confidence"])