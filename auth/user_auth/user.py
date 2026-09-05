from flask import flash, redirect, render_template, request, url_for, jsonify, session
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
import mysql.connector
from mysql.connector import Error

def student_admission():

    connection = None
    cursor = None

    try:
        student_name = request.form['student_name']
        dob = request.form['dob']
        gender = request.form['gender']
        department_id = request.form['department_id']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        cursor = connection.cursor()

        status = "PENDING"

        query = """
        INSERT INTO student_admission
        (student_name, dob, gender, department_id, email, phone, address, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (student_name, dob, gender, department_id, email, phone, address, status))
        connection.commit()
        flash("Application sent successfully.", "success")
        return redirect(url_for('index'))

    except Error as e:

        if connection:
            connection.rollback()

        print("MySQL Error in register():", e)
        flash(f"MySQL Error in register(): {e}", "danger")
        return redirect(url_for('index'))

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

        print("connection closed")


def student_login():
    connection = None
    cursor = None

    try:
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
                   SELECT sd.*
                   FROM student_detail sd
                   WHERE sd.student_id = %s
                     AND DATE_FORMAT(sd.dob, '%Y-%m-%d') = %s
                     AND UPPER(sd.status) = 'CONTINUE'
               """, (username, password))

        student = cursor.fetchone()

        if not student:
            flash("Student record not found.", "danger")
            return redirect(url_for("index", _anchor="login"))

        session["student_logged_in"] = True
        session["student_id"] = student["student_id"]

        return redirect(url_for("student_profile_page"))

    except (Error, KeyError) as error:
        print("MySQL Error in student_login():", error)
        flash("Student login could not be completed.", "danger")
        return redirect(url_for("index", _anchor="login"))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def student_profile():
    student_id = session.get("student_id")
    if not session.get("student_logged_in") or not student_id:
        return redirect(url_for("index", _anchor="login"))

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT sd.*
            FROM student_detail sd
            WHERE sd.student_id = %s
              AND UPPER(sd.status) = 'CONTINUE'
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            session.pop("student_logged_in", None)
            session.pop("student_id", None)
            flash("Student record not found", "danger")
            return redirect(url_for("index", _anchor="login"))

        return render_template("user/student.html", student=student)

    except Error as error:
        print("MySQL Error in student_profile():", error)
        flash("Could not load the student profile.", "danger")
        return redirect(url_for("index", _anchor="login"))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def chatbot():

    data = request.get_json()
    message = data.get("message", "").lower().strip()

    if "registration" in message or "register" in message:
        reply = (
            "To register, go to the Student Registration page "
            "and enter your personal, academic and contact details."
        )

    elif "document" in message or "documents" in message:
        reply = (
            "Required documents may include your HSC certificate, "
            "ID proof, passport-size photograph and transfer certificate."
        )

    elif "department" in message or "departments" in message:
        reply = (
            "Please check the Departments section to view the "
            "available courses and departments."
        )

    elif "status" in message or "enrollment" in message:
        reply = (
            "You can check your enrollment status using your "
            "Student ID in the Enrollment Status section."
        )

    elif "help" in message:
        reply = (
            "I can help you with Registration, Required Documents, "
            "Departments and Enrollment Status."
        )

    elif "hello" in message or "hi" in message or "hey" in message:
        reply = (
            "Hello! 👋 Welcome to the Enrollment Assistant. "
            "How can I help you?"
        )

    elif "login" in message or "logins" in message:
        reply = (
            "To Login, Go to Student Login Section."
            "Enter your student id or mobile number for username and dob for password to get login."
        )

    else:
        reply = (
            "Sorry, I didn't understand your question. "
            "You can ask about Registration, Documents, "
            "Departments or Enrollment Status."
        )

    return jsonify({
        "reply": reply
    })
