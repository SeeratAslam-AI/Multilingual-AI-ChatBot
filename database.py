"""
SafeX Solutions Chatbot - Module 3 Part A: Database + Logging
----------------------------------------------------------------------
Purpose: A tiny SQLite-based storage layer that records every single
chatbot interaction, automatically, with no manual intervention needed.

Why SQLite over a plain JSON file: the analytics module needs to do
things like "count how many times each question was asked" and "group
by category" - SQLite lets us do this with simple, reliable SQL queries
(GROUP BY, COUNT, ORDER BY) instead of writing that grouping logic by
hand over a growing JSON list every time.

Each row logged corresponds to exactly one user query, and stores
everything the task brief asks for:
  - the user's question
  - detected language
  - confidence score
  - whether it was answered or a fallback was given
  - timestamp

We also store a couple of extra fields (matched_faq_id, category,
final_response, response_type) because Module 3's own analytics
requirements (top questions, category interest, fallback list) need
them - all of this still comes for free from Module 1 + Module 2's
existing output, nothing new needs to be computed here.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = "chatbot_logs.db"


def init_db(db_path: str = DB_PATH) -> None:
    """
    Creates the query_logs table if it doesn't already exist.
    Safe to call every time the app starts - CREATE TABLE IF NOT EXISTS
    won't touch existing data.
    """
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question    TEXT NOT NULL,
            normalized_query TEXT,
            detected_language TEXT,
            confidence        REAL,
            response_type     TEXT,   -- 'answered' | 'hedged' | 'fallback'
            matched_faq_id    INTEGER,
            category          TEXT,
            final_response    TEXT,
            timestamp         TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@contextmanager
def get_connection(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def log_query(
    user_question: str,
    normalized_query: str,
    detected_language: str,
    confidence: float,
    response_type: str,
    matched_faq_id: int,
    category: str,
    final_response: str,
    db_path: str = DB_PATH,
) -> None:
    """
    Inserts one row for one chatbot interaction. This is called
    automatically by the /chat API endpoint (see main.py) right after
    Module 2 produces a response - the person calling the chatbot API
    never needs to think about logging at all.
    """
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO query_logs (
                user_question, normalized_query, detected_language,
                confidence, response_type, matched_faq_id, category,
                final_response, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_question,
                normalized_query,
                detected_language,
                confidence,
                response_type,
                matched_faq_id,
                category,
                final_response,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
