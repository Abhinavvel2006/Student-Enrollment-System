import pytest

from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.test_request_context():
            pass
        yield client


# -----------------------------
# BASIC ROUTE TESTS
# -----------------------------

def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200


def test_student_login_get(client):
    response = client.get("/student-login")

    assert response.status_code == 302
    assert "/#login" in response.location


def test_admin_login_get(client):
    response = client.get("/admin-login")

    assert response.status_code == 200


# -----------------------------
# STUDENT AUTHENTICATION
# -----------------------------

def test_student_profile_without_login(client):
    response = client.get("/student")

    assert response.status_code == 302
    assert "/#login" in response.location


def test_student_logout(client):
    with client.session_transaction() as session:
        session["student_logged_in"] = True
        session["student_id"] = "scc0001"

    response = client.get("/student-logout")

    assert response.status_code == 302


# -----------------------------
# ADMIN AUTHENTICATION
# -----------------------------

def test_admin_dashboard_without_login(client):
    response = client.get("/admin")

    assert response.status_code == 302


def test_admin_student_admission_without_login(client):
    response = client.post(
        "/student_admission",
        data={
            "student_name": "Test Student",
            "dob": "2000-01-01",
            "gender": "Male",
            "department_id": "1",
            "email": "test@example.com",
            "phone": "9999999999",
            "address": "Test Address"
        }
    )

    assert response.status_code == 302


def test_admin_logout(client):
    with client.session_transaction() as session:
        session["admin_logged_in"] = True
        session["admin_username"] = "admin"

    response = client.get("/admin_logout")

    assert response.status_code == 302


# -----------------------------
# CHATBOT TESTS
# -----------------------------

def test_chatbot_registration(client):
    response = client.post(
        "/chat",
        json={"message": "How can I register?"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "reply" in data
    assert "register" in data["reply"].lower()


def test_chatbot_documents(client):
    response = client.post(
        "/chat",
        json={"message": "What documents are required?"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "reply" in data
    assert "document" in data["reply"].lower()


def test_chatbot_department(client):
    response = client.post(
        "/chat",
        json={"message": "What departments are available?"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "reply" in data


def test_chatbot_help(client):
    response = client.post(
        "/chat",
        json={"message": "help"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "reply" in data


def test_chatbot_unknown_message(client):
    response = client.post(
        "/chat",
        json={"message": "xyzabc123"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "reply" in data


# -----------------------------
# INVALID ROUTES
# -----------------------------

def test_invalid_route(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404