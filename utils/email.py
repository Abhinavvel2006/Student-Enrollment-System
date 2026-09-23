import requests

from config import BREVO_API_KEY, BREVO_SENDER_EMAIL


def student_mail(name, email, student_id, password):
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

        data = {
            "sender": {
                "name": "Student Enrollment System",
                "email": BREVO_SENDER_EMAIL
            },
            "to": [
                {
                    "email": email,
                    "name": name
                }
            ],
            "subject": "Student Enrollment Accepted",
            "textContent": f"""
Hi {name},

Your admission application has been accepted.

You can now log in to the Student Login Portal.

Student ID : {student_id}
Password   : {password}

Thank you.

Student Enrollment System
"""
        }

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=15
        )

        if response.status_code == 201:
            result = response.json()

            print("Email sent successfully.")
            print("Brevo Message ID:", result.get("messageId"))

            return True

        print("Brevo email error:")
        print("Status:", response.status_code)
        print("Response:", response.text)

        return False

    except Exception as e:
        print("Email API error:", e)
        return False