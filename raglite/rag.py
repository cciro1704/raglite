"""Blueprint con le route dell'applicazione RAGlite."""

from __future__ import annotations

from flask import Blueprint, jsonify
from . import db 

bp = Blueprint("rag", __name__) 


@bp.get("/api/health")
def health():
    """Endpoint di verifica: l'app è in piedi?"""
    return jsonify({"ok": True, "version": "stub"})  

@bp.get("/api/stats")
def stats():
    """Conta gli elementi indicizzati nel database."""
    conn = db.get_db()
    docs_row = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()
    chunks_row = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
    emb_row = conn.execute("SELECT COUNT(*) AS n FROM embeddings").fetchone()
    return jsonify({
        "chunks_indexed": int(chunks_row["n"]),
        "docs_indexed": int(docs_row["n"]),
        "embeddings_indexed": int(emb_row["n"]),
    })