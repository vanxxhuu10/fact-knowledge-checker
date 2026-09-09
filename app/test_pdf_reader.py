from app.app.pdf_reader import extract_text_from_pdf


pdf_path = "data/test1.pdf"
output_path = "data/extracted.txt"

pages = extract_text_from_pdf(pdf_path)

with open(output_path, "w", encoding="utf-8") as file:
    for page in pages:
        file.write(f"\n{'=' * 70}\n")
        file.write(f"PAGE {page['page_number']}\n")
        file.write(f"{'=' * 70}\n\n")
        file.write(page["text"])
        file.write("\n")

print(f"Extracted text saved to: {output_path}")