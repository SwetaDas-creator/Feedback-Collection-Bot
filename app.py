from fastapi import FastAPI
from fastapi.responses import FileResponse
from textblob import TextBlob
from database import get_connection, create_table
import csv

app = FastAPI(title="Feedback Collection Bot")

create_table()

# ------------------ Utility Functions ------------------

def analyze_sentiment(text: str) -> str:
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    return "Neutral"


def detect_fraud(comment: str, nps: int) -> int:
    spam_words = ["ok", "good", "nice", "test", "aaa"]

    if len(comment.strip()) < 5:
        return 1

    if comment.lower() in spam_words:
        return 1

    if nps in [0, 10] and len(comment.split()) < 3:
        return 1

    return 0


def apply_scaledown(data: dict) -> dict:
    nps = data.get("nps")

    if nps >= 9:
        data["ces"] = None

    if nps <= 4:
        data["csat"] = None

    return data

# ------------------ APIs ------------------

@app.get("/")
def home():
    return {"message": "Feedback Collection Bot is running"}


@app.post("/submit")
def submit_feedback(data: dict):
    # ✅ SAFETY FIX: NPS validation
    nps = data.get("nps")
    if nps is None:
        return {"error": "NPS score is required"}

    data = apply_scaledown(data)

    comment = data.get("comment", "")
    sentiment = analyze_sentiment(comment)
    is_fraud = detect_fraud(comment, nps)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO feedback (nps, csat, ces, comment, sentiment, is_fraud)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("nps"),
            data.get("csat"),
            data.get("ces"),
            comment,
            sentiment,
            is_fraud
        )
    )

    conn.commit()
    conn.close()

    return {
        "status": "saved",
        "sentiment": sentiment,
        "fraud": bool(is_fraud)
    }


@app.get("/results")
def view_results():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "nps": row[1],
            "csat": row[2],
            "ces": row[3],
            "comment": row[4],
            "sentiment": row[5],
            "is_fraud": bool(row[6])
        })

    return {"total_responses": len(results), "data": results}


@app.get("/analytics")
def analytics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nps, csat FROM feedback WHERE is_fraud = 0")
    data = cursor.fetchall()
    conn.close()

    if not data:
        return {"message": "No valid feedback available"}

    promoters = sum(1 for nps, _ in data if nps >= 9)
    passives = sum(1 for nps, _ in data if 7 <= nps <= 8)
    detractors = sum(1 for nps, _ in data if nps <= 6)

    total = len(data)
    nps_score = ((promoters - detractors) / total) * 100

    valid_csats = [csat for _, csat in data if csat is not None]
    avg_csat = sum(valid_csats) / len(valid_csats) if valid_csats else 0

    return {
        "total_responses": total,
        "nps_score": round(nps_score, 2),
        "average_csat": round(avg_csat, 2),
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors
    }


@app.get("/insights")
def insights():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT sentiment FROM feedback WHERE is_fraud = 0")
    sentiments = cursor.fetchall()
    conn.close()

    total = len(sentiments)
    if total == 0:
        return {"message": "No valid feedback available"}

    positive = sum(1 for (s,) in sentiments if s == "Positive")
    neutral = sum(1 for (s,) in sentiments if s == "Neutral")
    negative = sum(1 for (s,) in sentiments if s == "Negative")

    if negative / total > 0.3:
        recommendation = "High negative feedback detected. Improve customer support."
    elif positive / total > 0.6:
        recommendation = "Strong positive sentiment. Focus on customer retention."
    else:
        recommendation = "Customer sentiment is stable. Monitor trends."

    return {
        "total_feedback": total,
        "positive_percent": round((positive / total) * 100, 2),
        "neutral_percent": round((neutral / total) * 100, 2),
        "negative_percent": round((negative / total) * 100, 2),
        "recommendation": recommendation
    }


@app.get("/trends")
def trends():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nps FROM feedback WHERE is_fraud = 0")
    scores = [row[0] for row in cursor.fetchall()]
    conn.close()

    if len(scores) < 4:
        return {"trend": "Not enough data"}

    midpoint = len(scores) // 2
    early_avg = sum(scores[:midpoint]) / midpoint
    recent_avg = sum(scores[midpoint:]) / (len(scores) - midpoint)

    trend = "Improving" if recent_avg > early_avg else "Declining"

    return {
        "trend": trend,
        "early_average_nps": round(early_avg, 2),
        "recent_average_nps": round(recent_avg, 2)
    }


@app.get("/fraud")
def view_fraud():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback WHERE is_fraud = 1")
    rows = cursor.fetchall()
    conn.close()

    # ✅ MANDATORY FIX: JSON formatting
    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "nps": r[1],
            "csat": r[2],
            "ces": r[3],
            "comment": r[4],
            "sentiment": r[5],
            "is_fraud": True
        })

    return {
        "fraud_count": len(data),
        "data": data
    }


@app.get("/export")
def export_csv():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback")
    rows = cursor.fetchall()
    conn.close()

    file_path = "feedback_export.csv"

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["ID", "NPS", "CSAT", "CES", "Comment", "Sentiment", "Is_Fraud"]
        )
        writer.writerows(rows)

    return FileResponse(
        file_path,
        media_type="text/csv",
        filename="feedback_export.csv"
    )
