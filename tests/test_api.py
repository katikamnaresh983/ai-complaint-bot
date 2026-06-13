from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
AUTH = ("admin", "admin123")


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_complaint_detects_category_and_priority():
    response = client.post(
        "/bot/analyze",
        auth=AUTH,
        json={
            "resident_name": "Asha",
            "message": "There is an urgent water leak on my street.",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["category"] == "Water Supply"
    assert body["priority"] == "Urgent"


def test_create_complaint_returns_ai_fields():
    response = client.post(
        "/complaints/",
        auth=AUTH,
        json={
            "resident_name": "Rahul",
            "message": "The power outage has continued since last night.",
        },
    )

    body = response.json()

    assert response.status_code == 201
    assert body["resident_name"] == "Rahul"
    assert body["category"] == "Electricity"
    assert body["status"] == "Open"
    assert body["suggested_response"]


def test_dashboard_stats_returns_counts():
    response = client.get("/dashboard/stats", auth=AUTH)

    body = response.json()

    assert response.status_code == 200
    assert "total" in body
    assert "categories" in body


def test_whatsapp_demo_creates_complaint_and_reply():
    response = client.post(
        "/whatsapp/demo",
        auth=AUTH,
        json={
            "resident_name": "Meera",
            "phone_number": "whatsapp:+911234567890",
            "apartment_unit": "C-301",
            "message": "The garbage has not been collected and the smell is bad.",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["complaint_id"]
    assert "Complaint #" in body["reply"]
    assert body["complaint"]["category"] == "Sanitation"


def test_whatsapp_webhook_returns_twiml_reply():
    response = client.post(
        "/whatsapp/webhook",
        data={
            "ProfileName": "Ravi Shah",
            "From": "whatsapp:+919999999999",
            "Body": "Flat A-101 has a power outage since morning",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "<Response><Message>Complaint #" in response.text


def test_dashboard_requires_login():
    response = client.get("/")

    assert response.status_code == 401
