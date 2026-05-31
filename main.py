import json
from fastapi import FastAPI, HTTPException
from schemas import PollCreate, Vote
from db import init, get_db

app = FastAPI()
init()


@app.post("/polls", status_code=201)
def create_poll(poll: PollCreate):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO polls (app_id, entity_id, question, options, created_by) VALUES (?, ?, ?, ?, ?)",
            (poll.app_id, poll.entity_id, poll.question, json.dumps(poll.options), poll.created_by)
        )
        db.commit()
    return {"poll_id": cur.lastrowid}


@app.get("/polls")
def list_polls(app_id: str, entity_id: str):
    with get_db() as db:
        polls = db.execute(
            "SELECT id, question, options, created_by, closed FROM polls WHERE app_id=? AND entity_id=?",
            (app_id, entity_id)
        ).fetchall()

        result = []
        for poll_id, question, options_json, created_by, closed in polls:
            options = json.loads(options_json)
            votes = db.execute(
                "SELECT option_index, user_id FROM votes WHERE poll_id=?",
                (poll_id,)
            ).fetchall()

            counts = [0] * len(options)
            voters = {}
            for option_index, user_id in votes:
                counts[option_index] += 1
                voters[user_id] = option_index

            result.append({
                "poll_id": poll_id,
                "question": question,
                "options": [{"index": i, "text": opt, "votes": counts[i]} for i, opt in enumerate(options)],
                "created_by": created_by,
                "voters": voters,
                "closed": bool(closed),
            })

    return result


@app.post("/polls/{poll_id}/close")
def close_poll(poll_id: int):
    with get_db() as db:
        cur = db.execute("UPDATE polls SET closed=1 WHERE id=?", (poll_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Poll not found")
        db.commit()
    return {"status": "closed"}


@app.post("/polls/{poll_id}/vote")
def cast_vote(poll_id: int, vote: Vote):
    with get_db() as db:
        poll = db.execute("SELECT options FROM polls WHERE id=?", (poll_id,)).fetchone()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        if vote.option_index >= len(json.loads(poll[0])):
            raise HTTPException(status_code=400, detail="Invalid option index")

        db.execute("""
        INSERT INTO votes (poll_id, user_id, option_index) VALUES (?, ?, ?)
        ON CONFLICT(poll_id, user_id) DO UPDATE SET option_index=excluded.option_index
        """, (poll_id, vote.user_id, vote.option_index))
        db.commit()

    return {"status": "voted"}


@app.delete("/polls/{poll_id}/vote")
def retract_vote(poll_id: int, user_id: str):
    with get_db() as db:
        cur = db.execute(
            "DELETE FROM votes WHERE poll_id=? AND user_id=?",
            (poll_id, user_id)
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vote not found")
        db.commit()

    return {"status": "retracted"}
