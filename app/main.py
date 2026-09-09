import os
import sys
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import (
    get_all_documents,
    get_document_facts,
    get_all_facts,
    get_all_relationships,
    reset_database
)
from pipeline import process_pdf
from relationship_pipeline import analyze_and_store_candidates

app = FastAPI(
    title="Fact Knowledge Layer API",
    description="Document-grounded fact extraction, evidence linking, and cross-document reasoning system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory setup
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Fact Knowledge Layer"}


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload PDF file, extract page-grounded facts, and analyze relationships."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = process_pdf(contents, filename=file.filename, auto_analyze=True)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/api/documents")
def list_documents():
    """List all uploaded documents with fact counts."""
    return get_all_documents()


@app.get("/api/documents/{document_id}")
def get_document(document_id: int):
    """Retrieve document details and extracted facts."""
    docs = [d for d in get_all_documents() if d["id"] == document_id]
    if not docs:
        raise HTTPException(status_code=404, detail="Document not found.")

    facts = get_document_facts(document_id)
    doc_info = docs[0]
    doc_info["facts"] = facts
    return doc_info


@app.get("/api/facts")
def list_facts(document_id: Optional[int] = None, subject: Optional[str] = None):
    """List and filter extracted facts."""
    all_facts = get_all_facts()
    if document_id is not None:
        all_facts = [f for f in all_facts if f["document_id"] == document_id]
    if subject:
        all_facts = [f for f in all_facts if subject.lower() in (f["subject"] or "").lower()]
    return all_facts


@app.get("/api/relationships")
def list_relationships(relationship_type: Optional[str] = Query(None, alias="type")):
    """List all detected relationships across documents."""
    return get_all_relationships(relationship_type=relationship_type)


@app.get("/api/relationships/{relationship_id}")
def get_relationship_detail(relationship_id: int):
    """Get single relationship detail with grounding evidence."""
    rels = get_all_relationships()
    target = [r for r in rels if r["id"] == relationship_id]
    if not target:
        raise HTTPException(status_code=404, detail="Relationship not found.")
    return target[0]


@app.post("/api/analysis/run")
def trigger_analysis():
    """Trigger cross-document candidate matching and relationship analysis."""
    try:
        results = analyze_and_store_candidates()
        return {
            "status": "success",
            "analyzed_count": len(results),
            "new_relationships": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/reset")
def reset_system():
    """Reset database tables (documents, facts, relationships)."""
    try:
        reset_database()
        return {"status": "success", "message": "Database reset clean."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


# Serve static web frontend at root
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_ui():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Fact Knowledge Layer API is running. Upload index.html to view UI."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
