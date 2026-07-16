"""
SafeX Solutions Chatbot - Module 3 Part B: Analytics
----------------------------------------------------------------------
Purpose: Turns the raw rows in query_logs (see database.py) into the
three things the brief asks the dashboard to show:
  1. Top 5-10 most asked questions
  2. Which service/category has the most interest
  3. A list of unanswered/fallback queries (useful for SafeX to see
     what users are asking that the bot currently cannot handle)
"""

from database import get_connection, DB_PATH


def get_top_questions(limit: int = 10, db_path: str = DB_PATH) -> list[dict]:
    """
    Groups logged questions by their exact text (lowercased, trimmed) and
    returns the most frequently asked ones with their counts.

    Note: this groups on the raw user_question text, not the matched FAQ,
    so two different phrasings of the "same" question are counted
    separately - which is actually useful here, since it shows SafeX
    the literal wording people use, not just which FAQ topic it maps to.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT LOWER(TRIM(user_question)) AS question,
                   COUNT(*) AS times_asked
            FROM query_logs
            GROUP BY LOWER(TRIM(user_question))
            ORDER BY times_asked DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_category_interest(db_path: str = DB_PATH) -> list[dict]:
    """
    Groups by matched FAQ category (Web Development, Cybersecurity,
    Digital Marketing, etc.) to show which services users ask about most.
    Fallback rows (no relevant category matched) are excluded, since
    "N/A" isn't a real service category - those show up separately in
    get_fallback_queries() instead.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT category, COUNT(*) AS query_count
            FROM query_logs
            WHERE response_type != 'fallback'
              AND category IS NOT NULL
              AND category != 'N/A'
            GROUP BY category
            ORDER BY query_count DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_fallback_queries(limit: int = 50, db_path: str = DB_PATH) -> list[dict]:
    """
    Returns the most recent queries that the bot could NOT confidently
    or plausibly answer (response_type = 'fallback', confidence below
    Module 1's relevance floor). This is the list SafeX can review to
    see what real questions the FAQ dataset is currently missing.

    Hedged ('closest info, not fully sure') queries are intentionally
    NOT included here - those did get answered, just with a hedge. Only
    genuinely unanswered queries belong in this list, per the brief.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT user_question, normalized_query, detected_language,
                   confidence, timestamp
            FROM query_logs
            WHERE response_type = 'fallback'
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_summary(db_path: str = DB_PATH) -> dict:
    """
    Convenience function bundling everything the dashboard (Module 4)
    is likely to want in one call, plus a couple of headline numbers.
    """
    with get_connection(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM query_logs").fetchone()["c"]
        answered = conn.execute(
            "SELECT COUNT(*) AS c FROM query_logs WHERE response_type = 'answered'"
        ).fetchone()["c"]
        hedged = conn.execute(
            "SELECT COUNT(*) AS c FROM query_logs WHERE response_type = 'hedged'"
        ).fetchone()["c"]
        fallback = conn.execute(
            "SELECT COUNT(*) AS c FROM query_logs WHERE response_type = 'fallback'"
        ).fetchone()["c"]

    return {
        "total_queries": total,
        "answered_count": answered,
        "hedged_count": hedged,
        "fallback_count": fallback,
        "top_questions": get_top_questions(10, db_path),
        "category_interest": get_category_interest(db_path),
        "fallback_queries": get_fallback_queries(50, db_path),
    }
