from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback
import threading
import importlib
from uuid import uuid4

from .intent_detector import detect_intent
from .automation_rules import decide_action
from .draft_store import save_draft
from .ticket_schema import create_ticket
from .email_adapter import send_email


app = FastAPI(title="RAG PoC - Index Retrieval (lazy init, package-safe)")

_singletons = {}
_singleton_lock = threading.Lock()

def ensure_module(module_name: str):
    try:
        return importlib.import_module(f"src.{module_name}")
    except ModuleNotFoundError:
        return importlib.import_module(module_name)

def get_embedding_model():
    if "emb_model" in _singletons:
        return _singletons["emb_model"]
    with _singleton_lock:
        mod = ensure_module("embeddings")
        EmbeddingModel = getattr(mod, "EmbeddingModel")
        _singletons["emb_model"] = EmbeddingModel()
        return _singletons["emb_model"]

def get_search_fn():
    if "search_fn" in _singletons:
        return _singletons["search_fn"]
    with _singleton_lock:
        for candidate in ("index_faiss", "index_sklearn"):
            try:
                mod = ensure_module(candidate)
                if hasattr(mod, "search"):
                    _singletons["search_fn"] = mod.search
                    _singletons["build_index_fn"] = getattr(mod, "build_index", None)
                    return _singletons["search_fn"]
            except ModuleNotFoundError:
                continue
        raise RuntimeError("No index backend available")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    user_email: str = "user@example.com"

@app.post("/query")
def query(req: QueryRequest):
    try:
        get_embedding_model()
        search_fn = get_search_fn()
        results = search_fn(req.query, top_k=req.top_k)

        if not results:
            raise RuntimeError("No retrieval results")

        intent = detect_intent(req.query)
        confidence = results[0]["score"]
        decision = decide_action(intent, confidence)

        ticket_id = str(uuid4())
        top_context = results[0]["meta"]["text"]

        automation = {"decision": decision}

        if decision in {"SAVE_DRAFT", "PENDING_APPROVAL"}:
            draft_path = save_draft(
                ticket_id=ticket_id,
                email={
                    "to": req.user_email,
                    "subject": f"Support: {intent.replace('_',' ').title()}"
                },
                body=top_context,
                confidence=confidence,
                status=decision
            )
            automation["draft_path"] = draft_path

        elif decision == "ESCALATE":
            ticket = create_ticket(
                user_email=req.user_email,
                subject=f"Escalated Issue: {intent}",
                message=req.query
            )
            automation["ticket"] = ticket.dict()

        return {
            "query": req.query,
            "intent": intent,
            "confidence": confidence,
            "decision": decision,
            "results": results,
            "automation": automation
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rebuild")
def rebuild():
    try:
        build_fn = _singletons.get("build_index_fn")
        if build_fn:
            build_fn("sample_docs")
            return {"status": "ok", "message": "index rebuilt"}
        raise RuntimeError("No index builder found")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
