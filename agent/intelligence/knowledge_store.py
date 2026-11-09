import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = "data/knowledge.db"


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            start_byte INTEGER NOT NULL,
            end_byte INTEGER NOT NULL,
            content TEXT NOT NULL,
            analysis TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id),
            UNIQUE(document_id, chunk_index)
        )
    """)
    db.commit()
    return db


def create_document(path, size_bytes):
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO documents (path, size_bytes, status, created_at) VALUES (?, ?, ?, ?)",
            (path, size_bytes, "processing",
             datetime.now(timezone.utc).isoformat())
        )
        return cursor.lastrowid


def save_chunk(document_id, chunk_index, start_byte,
               end_byte, content, analysis):
    with connect() as db:
        db.execute("""
            INSERT INTO chunks
            (document_id, chunk_index, start_byte, end_byte, content, analysis)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (document_id, chunk_index, start_byte,
              end_byte, content, analysis))


def finish_document(document_id, status="complete"):
    with connect() as db:
        db.execute(
            "UPDATE documents SET status = ? WHERE id = ?",
            (status, document_id)
        )


def get_document(document_id):
    with connect() as db:
        row = db.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,)
        ).fetchone()
        return row


def get_chunks(document_id):
    with connect() as db:
        return db.execute("""
            SELECT chunk_index, start_byte, end_byte, content, analysis
            FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_index
        """, (document_id,)).fetchall()
