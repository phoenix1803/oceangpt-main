from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/query")
def query(payload: dict):
    question = payload.get("question", "")
    # Placeholder: echo until RAG is wired
    return {"answer": f"Received: {question}", "sql": None}
