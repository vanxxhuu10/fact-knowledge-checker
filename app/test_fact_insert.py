from database import insert_document, insert_fact


document_id = insert_document("test_fact.pdf")

fact = {
    "subject": "Northstar Logistics",
    "property": "revenue",
    "attributes": {
        "value": 120,
        "unit": "million",
        "period": "FY2024"
    },
    "evidence": {
        "text": "Revenue for FY2024 was $120 million.",
        "page": 2,
        "document": "test_fact.pdf"
    }
}


fact_id = insert_fact(document_id, fact)

print("Inserted document ID:", document_id)
print("Inserted fact ID:", fact_id)