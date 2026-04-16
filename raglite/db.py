"""Gestione della connessione SQLite con Flask."""

from __future__ import annotations

import sqlite3

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Restituisce la connessione SQLite per la richiesta corrente."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e: Exception | None = None) -> None:
    """Chiude la connessione se esiste."""
    _ = e
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Crea lo schema e inserisce la sessione di default."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode("utf8"))
    db.execute("INSERT INTO sessions (name) VALUES (?)", ("Default Session",))
    db.commit()


@click.command("init-db")
def init_db_command() -> None:
    """Comando CLI: crea il database da zero."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app) -> None:
    """Registra teardown e comando CLI sull'app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)