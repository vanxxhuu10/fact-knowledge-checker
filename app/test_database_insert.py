from database import insert_document


document_id = insert_document("test1.pdf")

print("Inserted document ID:", document_id)