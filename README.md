# SafeX Solutions — Bilingual AI Chatbot & Analytics Dashboard

A full-stack, bilingual (English + Roman Urdu) customer support chatbot built for SafeX Solutions, a global technology and digital solutions company. The system understands user questions in either English or Roman Urdu, matches them against a curated FAQ knowledge base, and returns accurate answers with a measurable confidence score — all backed by a live analytics dashboard that shows what users are actually asking.

## Overview

The chatbot is built as four cooperating modules:

- **Core NLP / FAQ Matching Engine** — A TF-IDF + Cosine Similarity based matching engine over a 45-question bilingual FAQ dataset covering SafeX's services, pricing, contact details, cybersecurity, digital marketing, web development, and more. Every match comes with a confidence score between 0 and 1.

- **Bilingual Layer + Confidence Fallback** — Detects whether a message is written in English or Roman Urdu, normalizes Roman Urdu phrasing into English equivalents for better matching, and applies a three-tier confidence system: a confident direct answer, a hedged "closest match" answer with contact details, or an honest "I didn't understand" response for genuinely irrelevant input — so the bot never presents an unrelated answer as if it were relevant.

- **Backend, Logging & Analytics** — A FastAPI backend exposing a `/chat` endpoint that runs the full matching + bilingual pipeline and automatically logs every interaction (question, language, confidence, response type, timestamp) to a SQLite database, with no manual intervention required. Analytics endpoints surface the most frequently asked questions, which services generate the most interest, and a list of fallback queries the FAQ dataset currently can't answer.

- **Frontend — Chatbot UI & Analytics Dashboard** — A clean, responsive interface with a real-time chat window (color-coded responses by confidence tier) and an analytics dashboard with a bar chart of top questions, a pie chart of service interest, and a table of unanswered queries — all powered by live data from the backend.

## Key Features

- Understands mixed English / Roman Urdu input naturally
- Confidence-scored answers with graceful fallback handling instead of blind guessing
- Automatic, zero-touch interaction logging
- Live analytics dashboard for identifying gaps in the FAQ knowledge base
- One-click launcher script to start the backend and open the UI

## Tech Stack

Python, scikit-learn (TF-IDF, Cosine Similarity), FastAPI, SQLite, HTML/CSS/JavaScript, Chart.js
