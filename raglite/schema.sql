DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS chunks;
DROP TABLE IF EXISTS embeddings;

CREATE TABLE sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    source_type TEXT    NOT NULL DEFAULT 'text',
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
    UNIQUE (session_id, title)
);

CREATE TABLE messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role       TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
    kind       TEXT    NOT NULL CHECK(kind IN ('ingest', 'query')),
    content    TEXT    NOT NULL,
    parent_id  INTEGER DEFAULT NULL,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TEXT    DEFAULT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id)  REFERENCES messages (id) ON DELETE SET NULL
);

CREATE TABLE chunks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
    UNIQUE (document_id, chunk_index)
);

CREATE TABLE embeddings (
    chunk_id INTEGER PRIMARY KEY,
    vector   BLOB    NOT NULL,
    dim      INTEGER NOT NULL,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
);
CREATE INDEX idx_documents_session_id ON documents (session_id);
CREATE INDEX idx_messages_session_id  ON messages  (session_id);
CREATE INDEX idx_chunks_document_id   ON chunks    (document_id);