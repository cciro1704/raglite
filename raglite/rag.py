"""Blueprint con le route dell'applicazione RAGlite."""

from __future__ import annotations

from flask import Blueprint, jsonify
from . import db 
from datetime import datetime, timezone
from flask import Blueprint, current_app, jsonify, request
from .chunking import chunk_text
from .embedding import embed_text, vector_to_blob

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
@bp.post("/api/ingest")
def ingest():
    """Indicizza un documento nella sessione di default."""
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    text = (payload.get("text") or "").strip()

    # 1. text obbligatorio
    if not text:
        return jsonify({"error": "text is required"}), 400

    # 2. title automatico se assente
    if not title:
        title = "doc-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    conn = db.get_db()

    # 3. Recupera la Default Session dal database
    session_row = conn.execute(
        "SELECT id FROM sessions WHERE name = ?", ("Default Session",)
    ).fetchone()

    # 4. Sessione non trovata
    if session_row is None:
        return jsonify({"error": "default session not found"}), 500

    session_id = session_row["id"]

    # 5. Inserisci il document
    cur = conn.execute(
        "INSERT INTO documents (session_id, title) VALUES (?, ?)",
        (session_id, title),
    )
    document_id = cur.lastrowid

    # 6. Calcola i chunk usando la configurazione dell'app
    size = current_app.config["RAG_CHUNK_SIZE"]
    overlap = current_app.config["RAG_CHUNK_OVERLAP"]
    chunks = chunk_text(text, size, overlap)

    # 7. Inserisci chunks e embeddings
    chunks_indexed = 0
    embeddings_indexed = 0

    for chunk_index, chunk_str in chunks:
        cur = conn.execute(
            "INSERT INTO chunks (document_id, chunk_index, text) VALUES (?, ?, ?)",
            (document_id, chunk_index, chunk_str),
        )
        chunk_id = cur.lastrowid
        chunks_indexed += 1

        vector = embed_text(chunk_str)
        blob = vector_to_blob(vector)
        conn.execute(
            "INSERT INTO embeddings (chunk_id, vector, dim) VALUES (?, ?, ?)",
            (chunk_id, blob, len(vector)),
        )
        embeddings_indexed += 1

    # 8. Commit e risposta
    conn.commit()

    return jsonify({
        "title": title,
        "document_id": document_id,
        "chunks_indexed": chunks_indexed,
        "embeddings_indexed": embeddings_indexed,
    })