from fastapi import FastAPI
from datetime import date
from models import MemoryItem, Feedback
from engine import review
from db import connect, init_db
from graph import compute_centrality

app = FastAPI(title="Echo Memory Engine", version="0.1.0")

conn = connect()
init_db(conn)


@app.get("/health")
def health():
    return {"status": "alive", "version": "Echo v0.1.0"}


@app.post("/memory")
def upsert_memory(payload: dict):
    cur = conn.cursor()

    # Insert or update the item (for update, we need to handle centrality recompute)
    cur.execute("""
    INSERT OR REPLACE INTO memory_items (
        id, source, note_path, block_ref,
        interval, ease, confidence, repetitions, centrality,
        last_review, next_review, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload["id"],
        payload["source"],
        payload["note_path"],
        payload.get("block_ref"),
        1.0,
        2.5,
        0.5,
        0,
        0.0,  # initial centrality
        None,  # last_review
        date.today(),  # next_review
        date.today()  # created_at
    ))

    # Recompute centrality for all items
    cur.execute("SELECT id, source, note_path FROM memory_items")
    all_items = [{"id": row[0], "source": row[1], "note_path": row[2]} for row in cur.fetchall()]
    centrality_scores = compute_centrality(all_items)
    
    # Update centrality for all
    for item_id, score in centrality_scores.items():
        cur.execute("UPDATE memory_items SET centrality = ? WHERE id = ?", (score, item_id))

    conn.commit()
    return {"status": "ok"}


@app.get("/reviews/today")
def reviews_today():
    cur = conn.cursor()
    today = date.today()
    
    cur.execute("""
    SELECT id, source, note_path, block_ref, interval, ease, confidence, repetitions, centrality, last_review, next_review
    FROM memory_items
    WHERE next_review <= ?
    ORDER BY centrality DESC, next_review ASC
    """, (today,))
    
    rows = cur.fetchall()
    reviews = []
    for row in rows:
        reviews.append({
            "id": row[0],
            "source": row[1],
            "note_path": row[2],
            "block_ref": row[3],
            "interval": row[4],
            "ease": row[5],
            "confidence": row[6],
            "repetitions": row[7],
            "centrality": row[8],
            "last_review": row[9],
            "next_review": row[10]
        })
    
    return reviews


@app.post("/review")
def submit_review(payload: dict):
    item_id = payload["id"]
    feedback = Feedback(payload["feedback"])
    today = date.today()
    
    cur = conn.cursor()
    
    # Fetch current item
    cur.execute("""
    SELECT id, source, note_path, block_ref, interval, ease, confidence, repetitions, last_review, next_review
    FROM memory_items
    WHERE id = ?
    """, (item_id,))
    
    row = cur.fetchone()
    if not row:
        return {"error": "Memory item not found"}
    
    # Reconstruct MemoryItem
    item = MemoryItem(
        id=row[0],
        source=row[1],
        note_path=row[2],
        block_ref=row[3],
        interval=row[4],
        ease=row[5],
        confidence=row[6],
        repetitions=row[7],
        last_review=row[8] if row[8] else None,
        next_review=row[9]
    )
    
    # Apply review
    updated_item = review(item, feedback, today)
    
    # Update item in DB
    cur.execute("""
    UPDATE memory_items
    SET interval = ?, ease = ?, confidence = ?, repetitions = ?, last_review = ?, next_review = ?
    WHERE id = ?
    """, (
        updated_item.interval,
        updated_item.ease,
        updated_item.confidence,
        updated_item.repetitions,
        updated_item.last_review,
        updated_item.next_review,
        item_id
    ))
    
    # Insert into review_history
    cur.execute("""
    INSERT INTO review_history (memory_id, review_date, feedback, interval_after, ease_after, confidence_after)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        item_id,
        today,
        feedback.value,
        updated_item.interval,
        updated_item.ease,
        updated_item.confidence
    ))
    
    conn.commit()
    return {"status": "ok", "next_review": updated_item.next_review.isoformat()}
