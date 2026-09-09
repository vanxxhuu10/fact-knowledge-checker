import os
from pdf_reader import extract_text_from_pdf, calculate_file_hash
from fact_extractor import extract_facts
from fact_normalizer import normalize_fact
from database import insert_document, insert_fact, get_document_by_hash, get_document_facts
from relationship_pipeline import analyze_and_store_candidates


def process_pdf(pdf_path_or_bytes, filename=None, auto_analyze=True):
    """
    Process PDF file or raw bytes:
    1. Content hash check for deduplication
    2. Page-aware text extraction
    3. LLM fact extraction with evidence
    4. Database storage
    5. Incremental cross-document candidate matching & relationship analysis
    """
    if isinstance(pdf_path_or_bytes, str):
        document_name = filename or os.path.basename(pdf_path_or_bytes)
    else:
        document_name = filename or "uploaded_document.pdf"

    # 1. Content Hashing & Deduplication
    file_hash = calculate_file_hash(pdf_path_or_bytes)
    existing_doc = get_document_by_hash(file_hash)
    if existing_doc:
        doc_id = existing_doc["id"]
        existing_facts = get_document_facts(doc_id)
        return {
            "document_id": doc_id,
            "filename": existing_doc["filename"],
            "already_processed": True,
            "facts_extracted": len(existing_facts),
            "facts": existing_facts,
            "new_relationships": []
        }

    # 2. Page-Aware Text Extraction
    pages = extract_text_from_pdf(pdf_path_or_bytes)

    # 3. Document Persistence
    document_id = insert_document(document_name, file_hash=file_hash)

    all_facts = []

    # 4. Page-by-Page Fact Extraction & Normalization
    for page in pages:
        raw_facts = extract_facts(page["text"])

        for raw_fact in raw_facts:
            fact = normalize_fact(
                raw_fact,
                page_number=page["page_number"],
                document_name=document_name
            )

            fact_id = insert_fact(document_id, fact)
            fact["id"] = fact_id
            all_facts.append(fact)

    # 5. Incremental Cross-Document Relationship Analysis
    new_relationships = []
    if auto_analyze:
        try:
            new_relationships = analyze_and_store_candidates(target_document_id=document_id)
        except Exception as e:
            print(f"Warning: Relationship analysis encountered error: {e}")

    return {
        "document_id": document_id,
        "filename": document_name,
        "already_processed": False,
        "facts_extracted": len(all_facts),
        "facts": all_facts,
        "new_relationships": new_relationships
    }