from .schemas import ComplaintAnalysis


CATEGORY_KEYWORDS = {
    "Water Supply": {"water", "tap", "pipe", "leak", "drainage", "sewage", "flood"},
    "Electricity": {"electricity", "power", "light", "outage", "wire", "transformer"},
    "Sanitation": {"garbage", "trash", "waste", "dirty", "cleaning", "smell"},
    "Roads": {"road", "pothole", "traffic", "street", "footpath", "parking"},
    "Noise": {"noise", "loud", "music", "construction", "disturbance"},
    "Safety": {"unsafe", "crime", "theft", "harassment", "accident", "danger"},
}

URGENT_WORDS = {"urgent", "emergency", "danger", "unsafe", "fire", "flood", "accident"}
HIGH_WORDS = {"broken", "blocked", "leak", "outage", "sewage", "harassment"}
NEGATIVE_WORDS = {"angry", "frustrated", "upset", "bad", "terrible", "ignored", "unhappy"}
POSITIVE_WORDS = {"thanks", "thank", "appreciate", "resolved", "good"}


def analyze_complaint(message: str, category_hint: str | None = None) -> ComplaintAnalysis:
    text = message.lower()
    words = set(text.replace(".", " ").replace(",", " ").split())

    category = category_hint or _detect_category(words)
    priority = _detect_priority(words)
    sentiment = _detect_sentiment(words)
    summary = _summarize(message, category)
    suggested_response = _suggest_response(category, priority)

    return ComplaintAnalysis(
        category=category,
        priority=priority,
        sentiment=sentiment,
        summary=summary,
        suggested_response=suggested_response,
    )


def _detect_category(words: set[str]) -> str:
    best_category = "General"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = len(words.intersection(keywords))
        if score > best_score:
            best_category = category
            best_score = score

    return best_category


def _detect_priority(words: set[str]) -> str:
    if words.intersection(URGENT_WORDS):
        return "Urgent"
    if words.intersection(HIGH_WORDS):
        return "High"
    if len(words) < 12:
        return "Low"
    return "Medium"


def _detect_sentiment(words: set[str]) -> str:
    negative_hits = len(words.intersection(NEGATIVE_WORDS))
    positive_hits = len(words.intersection(POSITIVE_WORDS))

    if negative_hits > positive_hits:
        return "Negative"
    if positive_hits > negative_hits:
        return "Positive"
    return "Neutral"


def _summarize(message: str, category: str) -> str:
    cleaned = " ".join(message.split())
    if len(cleaned) > 140:
        cleaned = f"{cleaned[:137].rstrip()}..."
    return f"{category} complaint: {cleaned}"


def _suggest_response(category: str, priority: str) -> str:
    prefix = "We have logged your complaint"
    if priority in {"Urgent", "High"}:
        prefix = "We have prioritized your complaint"
    return f"{prefix} under {category}. Our team will review it and share an update soon."
