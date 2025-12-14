from datetime import date, timedelta
from models import MemoryItem, Feedback
from engine import review


def test_saturn_30_days_simulation():
    today = date(2025, 1, 1)

    item = MemoryItem(
        id="test-graph-theory",
        source="obsidian",
        note_path="Graphes.md",
        block_ref="definition"
    )

    log = []

    for day in range(30):
        current_day = today + timedelta(days=day)

        # Règle simple de feedback simulé
        if day < 5:
            feedback = Feedback.FORGOT
        elif day < 15:
            feedback = Feedback.FUZZY
        else:
            feedback = Feedback.MASTERED

        if item.next_review is None or current_day >= item.next_review:
            item = review(item, feedback, current_day)

            log.append({
                "day": day,
                "feedback": feedback.value,
                "interval": round(item.interval, 2),
                "ease": round(item.ease, 2),
                "confidence": round(item.confidence, 2),
                "next_review": item.next_review
            })

    # Assertions clés (invariants)
    assert item.ease >= 1.3
    assert 0.2 <= item.confidence <= 1.0
    assert item.interval >= 1.0
    assert item.repetitions > 0
