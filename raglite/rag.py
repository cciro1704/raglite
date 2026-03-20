"""Blueprint con le route dell'applicazione RAGlite."""

from __future__ import annotations

from flask import Blueprint, jsonify

bp = Blueprint("rag", __name__) 


@bp.get("/api/health")
def health():
    """Endpoint di verifica: l'app è in piedi?"""
    return jsonify({"ok": True, "version": "stub"})  