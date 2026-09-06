from unittest.mock import MagicMock, patch

from flask import session
from mysql.connector import Error

from main import app


# =========================================================
# ADMIN LOGIN DATABASE TESTS
# =========================================================

@patch("auth.admin_auth.admin.mysql.connector.connect")
def test_admin_login_success(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = (
        1,
        "admin",
        "password"
    )

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        response = client.post(
            "/admin-login",
            data={
                "admin_username": "admin",
                "admin_password": "password"
            }
        )

        assert response.status_code == 302
        assert "/admin" in response.location

        with client.session_transaction() as sess:
            assert sess["admin_logged_in"] is True
            assert sess["admin_username"] == "admin"

        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()


@patch("auth.admin_auth.admin.mysql.connector.connect")
def test_admin_login_invalid(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = None

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        response = client.post(
            "/admin-login",
            data={
                "admin_username": "wrong",
                "admin_password": "wrong"
            }
        )

        assert response.status_code == 302
        assert "/admin-login" in response.location


@patch("auth.admin_auth.admin.mysql.connector.connect")
def test_admin_login_database_error(mock_connect):

    mock_connect.side_effect = Error("Database connection failed")

    with app.test_client() as client:

        response = client.post(
            "/admin-login",
            data={
                "admin_username": "admin",
                "admin_password": "password"
            }
        )

        assert response.status_code == 302
        assert "/admin-login" in response.location


# =========================================================
# STUDENT LOGIN DATABASE TESTS
# =========================================================

@patch("auth.user_auth.user.mysql.connector.connect")
def test_student_login_success(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = {
        "student_id": "scc0001",
        "student_name": "Test Student",
        "status": "CONTINUE"
    }

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        response = client.post(
            "/student-login",
            data={
                "username": "scc0001",
                "password": "2000-01-01"
            }
        )

        assert response.status_code == 302
        assert "/student" in response.location

        with client.session_transaction() as sess:
            assert sess["student_logged_in"] is True
            assert sess["student_id"] == "scc0001"

        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()


@patch("auth.user_auth.user.mysql.connector.connect")
def test_student_login_invalid(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = None

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        response = client.post(
            "/student-login",
            data={
                "username": "wrong",
                "password": "wrong"
            }
        )

        assert response.status_code == 302
        assert "#login" in response.location


@patch("auth.user_auth.user.mysql.connector.connect")
def test_student_login_database_error(mock_connect):

    mock_connect.side_effect = Error("Database connection failed")

    with app.test_client() as client:

        response = client.post(
            "/student-login",
            data={
                "username": "scc0001",
                "password": "2000-01-01"
            }
        )

        assert response.status_code == 302
        assert "#login" in response.location


# =========================================================
# STUDENT DISCONTINUE DATABASE TESTS
# =========================================================

@patch("auth.admin_auth.admin.mysql.connector.connect")
def test_discontinue_student_success(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.rowcount = 1

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        with client.session_transaction() as sess:
            sess["admin_logged_in"] = True

        response = client.post(
            "/admin/students/scc0001/discontinue"
        )

        assert response.status_code == 302

        # Database transaction must be committed
        mock_connection.commit.assert_called_once()

        # UPDATE + DELETE should both be executed
        assert mock_cursor.execute.call_count == 2


@patch("auth.admin_auth.admin.mysql.connector.connect")
def test_discontinue_student_not_found(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.rowcount = 0

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        with client.session_transaction() as sess:
            sess["admin_logged_in"] = True

        response = client.post(
            "/admin/students/scc9999/discontinue"
        )

        assert response.status_code == 302

        # Because student was not found, transaction should rollback
        mock_connection.rollback.assert_called_once()

        # Nothing should be committed
        mock_connection.commit.assert_not_called()


# =========================================================
# APPLICATION REJECT DATABASE TEST
# =========================================================

@patch("auth.admin_auth.admin.mysql.connector.connect")
def test_reject_application(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = {
        "application_id": 1,
        "student_name": "Test Student",
        "dob": "2000-01-01",
        "gender": "Male",
        "department_id": 1,
        "email": "test@example.com",
        "phone": "9999999999",
        "address": "Test Address",
        "department_name": "Computer Science"
    }

    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1

    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        with client.session_transaction() as sess:
            sess["admin_logged_in"] = True

        response = client.post(
            "/admin/applications/1/reject"
        )

        assert response.status_code == 302

        mock_connection.commit.assert_called_once()


# =========================================================
# APPLICATION ACCEPT DATABASE TEST
# =========================================================

@patch("auth.admin_auth.admin.mysql.connector.connect")
def test_accept_application(mock_connect):

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    # fetchone() is called multiple times:
    #
    # 1. application
    # 2. GET_LOCK result
    # 3. latest student
    # 4. duplicate application check

    mock_cursor.fetchone.side_effect = [
        {
            "application_id": 1,
            "student_name": "Test Student",
            "dob": "2000-01-01",
            "gender": "Male",
            "department_id": 1,
            "email": "test@example.com",
            "phone": "9999999999",
            "address": "Test Address",
            "department_name": "Computer Science"
        },
        {
            "acquired": 1
        },
        None,
        None,
        None
    ]

    mock_cursor.rowcount = 1

    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    with app.test_client() as client:

        with client.session_transaction() as sess:
            sess["admin_logged_in"] = True

        response = client.post(
            "/admin/applications/1/accept"
        )

        assert response.status_code == 302

        # Acceptance must commit all database changes
        mock_connection.commit.assert_called_once()

        # Multiple SQL operations should have happened
        assert mock_cursor.execute.call_count >= 5