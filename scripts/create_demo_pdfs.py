import os
import pymupdf


def create_pdf(filename, title, content_paragraphs):
    """Generate a clean PDF document with text using PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842) # A4 size
    
    # Title
    page.insert_text((50, 60), title, fontsize=18, fontname="helv", color=(0.1, 0.2, 0.6))
    
    y = 110
    for para in content_paragraphs:
        page.insert_text((50, y), para, fontsize=12, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 30
        
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc.save(filename)
    doc.close()
    print(f"Created PDF: {filename}")


def generate_all_demo_pdfs():
    base_dir = r"data/demo"

    # Case 1: Corroboration
    create_pdf(
        os.path.join(base_dir, "case1_corroboration_docA.pdf"),
        "Northstar Logistics Annual Summary FY2024",
        [
            "Northstar Logistics generated revenue of $120 million in FY2024.",
            "The company expanded operational coverage across major logistics corridors."
        ]
    )
    create_pdf(
        os.path.join(base_dir, "case1_corroboration_docB.pdf"),
        "Northstar Logistics Limited Financial Report FY2024",
        [
            "Northstar Logistics Limited reported FY2024 revenue of USD 120M.",
            "Operating margins improved steadily throughout the fiscal year."
        ]
    )

    # Case 2: Genuine Contradiction
    create_pdf(
        os.path.join(base_dir, "case2_contradiction_docA.pdf"),
        "Northstar Workforce Report 2024 (Source A)",
        [
            "Northstar Logistics had 4,800 employees in FY2024.",
            "Workforce safety programs were successfully implemented across all hubs."
        ]
    )
    create_pdf(
        os.path.join(base_dir, "case2_contradiction_docB.pdf"),
        "Northstar Workforce Audit 2024 (Source B)",
        [
            "Northstar Logistics Limited had 6,200 employees in FY2024.",
            "Employee benefits and headcount expansion were highlighted in the audit."
        ]
    )

    # Case 3: Contextual Difference
    create_pdf(
        os.path.join(base_dir, "case3_contextual_docA.pdf"),
        "Northstar Logistics Historical Overview FY2023",
        [
            "Revenue was $95M in FY2023.",
            "The organization streamlined operational expenditure during the fiscal period."
        ]
    )
    create_pdf(
        os.path.join(base_dir, "case3_contextual_docB.pdf"),
        "Northstar Logistics Historical Overview FY2024",
        [
            "Revenue was $120M in FY2024.",
            "Increased parcel volume drove significant revenue expansion."
        ]
    )

    # Case 4: Reasoning Failure / Ambiguity
    create_pdf(
        os.path.join(base_dir, "case4_ambiguity_failure.pdf"),
        "Northstar Strategic Planning Note",
        [
            "Northstar Logistics engineering organization is evaluating potential regional expansion.",
            "Specific revenue targets and headcount numbers for this potential project remain unannounced and undecided."
        ]
    )


if __name__ == "__main__":
    generate_all_demo_pdfs()
