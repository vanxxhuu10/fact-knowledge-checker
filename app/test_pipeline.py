from app.app.pipeline import process_pdf


pdf_path = "data/test1.pdf"

facts = process_pdf(pdf_path)

print("Total facts:", len(facts))

for i, fact in enumerate(facts[:10], start=1):
    print(f"\nFACT {i}")

    print("Subject:", fact["subject"])
    print("Property:", fact["property"])

    print("Attributes:")
    print("  Value:", fact["attributes"]["value"])
    print("  Unit:", fact["attributes"]["unit"])
    print("  Period:", fact["attributes"]["period"])

    print("Evidence:")
    print("  Text:", fact["evidence"]["text"])
    print("  Page:", fact["evidence"]["page"])
    print("  Document:", fact["evidence"]["document"])