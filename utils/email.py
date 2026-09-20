import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import smtp_server, smtp_user, smtp_password, smtp_port

def student_mail(name, email, student_id, password):

    try:
        message = MIMEMultipart()
        message["From"] = smtp_user
        message["To"] = email
        message["Subject"] = "Student Enrollment Accepted"

        body = f"""
Hi {name},

Your admission application has been accepted.

You can now log in to the Student Login Portal.

Student ID : {student_id}
Password   : {password}

Thank you.

Student Enrollment System
"""

        message.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        server.login(smtp_user, smtp_password)

        server.sendmail(smtp_user, email, message.as_string())

        server.quit()

        print(f"Email sent successfully to {email}")
        return True

    except smtplib.SMTPException as e:
        print("Email not sent", e)
        return False