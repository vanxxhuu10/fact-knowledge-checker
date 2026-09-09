import os

from pipeline import process_pdf


DATA_FOLDER = "data"


for filename in os.listdir(DATA_FOLDER):

    if filename.lower().endswith(".pdf"):

        pdf_path = os.path.join(DATA_FOLDER, filename)

        print(f"\nProcessing: {filename}")

        facts = process_pdf(pdf_path)

        print(f"Extracted {len(facts)} facts")