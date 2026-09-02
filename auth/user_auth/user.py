from flask import  flash, redirect, request, url_for, jsonify
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
