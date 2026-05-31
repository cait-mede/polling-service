# Polling Service

## Overview

A generic polling microservice built with FastAPI and SQLite. Supports creating polls with multiple options, casting and updating votes, and retrieving results with live vote counts.

Polls are scoped by `app_id` and `entity_id` so the service can be reused across different applications and contexts (e.g. different book clubs, different groups).

## Data Model

Each **poll**:
- `app_id` — identifies the calling application (e.g. `"book_club"`)
- `entity_id` — identifies what the poll belongs to (e.g. a group ID)
- `question` — the poll question
- `options` — list of choices (minimum 2)
- `created_by` — user ID of the creator

Each **vote**:
- One vote per user per poll
- Submitting a new vote overwrites the previous one (upsert)

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the server (runs on port 8001):
```bash
python -m uvicorn main:app --port 8001 --reload
```

---

## API

### POST /polls — Create a poll

**Body:**
```json
{
  "app_id": "book_club",
  "entity_id": "42",
  "question": "What should we read next?",
  "options": ["Dune", "Ender's Game", "Hyperion"],
  "created_by": "user123"
}
```

**Response:**
```json
{ "poll_id": 1 }
```

**Example:**
```bash
curl -X POST http://localhost:8001/polls \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "book_club",
    "entity_id": "42",
    "question": "What should we read next?",
    "options": ["Dune", "Enders Game", "Hyperion"],
    "created_by": "user123"
  }'
```

---

### GET /polls — List polls for an entity

**Query params:** `app_id`, `entity_id`

**Response:** Array of polls with options and live vote counts.
```json
[
  {
    "poll_id": 1,
    "question": "What should we read next?",
    "options": [
      { "index": 0, "text": "Dune", "votes": 2 },
      { "index": 1, "text": "Ender's Game", "votes": 1 },
      { "index": 2, "text": "Hyperion", "votes": 0 }
    ],
    "created_by": "user123",
    "voters": { "user123": 0, "user456": 1 }
  }
]
```

**Example:**
```bash
curl "http://localhost:8001/polls?app_id=book_club&entity_id=42"
```

---

### POST /polls/{poll_id}/vote — Cast or update a vote

**Body:**
```json
{ "user_id": "user456", "option_index": 1 }
```

**Response:**
```json
{ "status": "voted" }
```

Submitting again with a different `option_index` updates the vote.

**Example:**
```bash
curl -X POST http://localhost:8001/polls/1/vote \
  -H "Content-Type: application/json" \
  -d '{ "user_id": "user456", "option_index": 1 }'
```

---

### DELETE /polls/{poll_id}/vote — Retract a vote

**Query param:** `user_id`

**Response:**
```json
{ "status": "retracted" }
```

Returns 404 if the user has not voted on this poll.

**Example:**
```bash
curl -X DELETE "http://localhost:8001/polls/1/vote?user_id=user456"
```
