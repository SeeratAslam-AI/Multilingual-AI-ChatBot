"""
SafeX Solutions Chatbot - Module 3 Part C: Backend API
----------------------------------------------------------------------
Purpose: The "bridge" between the chatbot logic (Modules 1 + 2) and
the outside world - the chat widget (Module 4's frontend) talks to
this API, and so does the analytics dashboard.

Two groups of endpoints:
  1. POST /chat            - send a user message, get a bot reply.
                              Every call is automatically logged - no
                              manual logging needed anywhere else.
  2. GET  /analytics/...   - data for the dashboard (top questions,
                              category interest, fallback queries).

Run locally with:
    uvicorn main:app --reload

Then visit http://127.0.0.1:8000/docs for interactive API docs
(FastAPI generates this automatically).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from response_manager import SafeXResponseManager
from database import init_db, log_query
import analytics

app = FastAPI(title="SafeX Solutions Chatbot API")

# Allow the frontend (Module 4) to call this API from a browser,
# regardless of which port/domain it's served from during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loaded once at startup - Module 1's FAQ engine + Module 2's bilingual
# wrapper are both wrapped inside this single object.
response_manager = SafeXResponseManager("faqs.json")

# Ensure the table exists as soon as this module is imported (not just
# on the "startup" event) - CREATE TABLE IF NOT EXISTS is safe to call
# repeatedly and this way logging works correctly whether the app is
# run via uvicorn or driven through a test client.
init_db()


@app.on_event("startup")
def on_startup():
    init_db()


# --------------------------------------------------------------------
# Request / response schemas
# --------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    user_message: str
    detected_language: str
    confidence: float
    response_type: str
    category: str
    final_response: str


# --------------------------------------------------------------------
# Chat endpoint
# --------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Receives a user's message, runs it through Module 1 + Module 2,
    logs the interaction automatically, and returns the bot's reply.
    """
    result = response_manager.get_response(request.message)

    log_query(
        user_question=result["user_message"],
        normalized_query=result["normalized_query"],
        detected_language=result["detected_language"],
        confidence=result["confidence"],
        response_type=result["response_type"],
        matched_faq_id=result["faq_id"],
        category=result["category"],
        final_response=result["final_response"],
    )

    return ChatResponse(
        user_message=result["user_message"],
        detected_language=result["detected_language"],
        confidence=result["confidence"],
        response_type=result["response_type"],
        category=result["category"],
        final_response=result["final_response"],
    )


# --------------------------------------------------------------------
# Analytics endpoints (for Module 4's dashboard)
# --------------------------------------------------------------------
@app.get("/analytics/summary")
def analytics_summary():
    """Everything the dashboard needs in a single call."""
    return analytics.get_summary()


@app.get("/analytics/top-questions")
def analytics_top_questions(limit: int = 10):
    return {"top_questions": analytics.get_top_questions(limit)}


@app.get("/analytics/categories")
def analytics_categories():
    return {"category_interest": analytics.get_category_interest()}


@app.get("/analytics/fallback-queries")
def analytics_fallback_queries(limit: int = 50):
    return {"fallback_queries": analytics.get_fallback_queries(limit)}


@app.get("/")
def root():
    """
    Serves the frontend (index.html) directly, so opening
    http://127.0.0.1:8000 in a browser shows the chat + dashboard UI
    itself, not a JSON status message.
    """
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "SafeX Chatbot API is running, but index.html was not found in this folder."}


@app.get("/status")
def status():
    """Simple health-check endpoint, separate from the UI now living at '/'."""
    return {"status": "SafeX Chatbot API is running", "docs": "/docs"}