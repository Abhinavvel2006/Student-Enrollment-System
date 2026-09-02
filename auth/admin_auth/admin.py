from flask import flash, redirect, render_template, request, url_for, session
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
import mysql.connector
from mysql.connector import Error

def admin_login():

    connection = None
    cursor = None

    try:
        admin_username = request.form["admin_username"]
        admin_password = request.form["admin_password"]
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        cursor = connection.cursor()

        query = """
            SELECT * FROM admin
            WHERE admin_username = %s
            AND admin_password = %s
        """

        cursor.execute(query, (admin_username, admin_password))

        admin = cursor.fetchone()

        if admin:
            session["admin_logged_in"] = True
            session["admin_username"] = admin_username

            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin username or password", "danger")
        return redirect(url_for("admin_login_page"))

    except Error as e:

        print("Database Error:", e)
        flash("Database error occurred", "danger")

        return redirect(url_for("admin_login_page"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

        print("Connection closed")


def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login_page"))

    connection = None
    cursor = None

    try:

        # filter
        search = request.args.get("search", "").strip()
        department = request.args.get("department", "").strip()
        status = request.args.get("status", "").strip()
        selected_date = request.args.get("date", "").strip()


        connection = mysql.connector.connect(
            host = MYSQL_HOST,
            user = MYSQL_USER,
            password = MYSQL_PASSWORD,
            database = MYSQL_DATABASE
        )

        cursor = connection.cursor(dictionary=True)

        # total
        query1 = """
        select count(*) as total
        from student_admission
        """

        cursor.execute(query1)
        total_applicant = cursor.fetchone()["total"]

        # pending
        query2 = """
        select count(*) as pending
        from student_admission
        where status = 'PENDING'
        """

        cursor.execute(query2)
        pending_applicant = cursor.fetchone()["pending"]

        # accepted
        query3 = """
        select count(*) as accepted
        from student_admission
        where status = 'ACCEPTED'
        """

        cursor.execute(query3)
        accepted_applicant = cursor.fetchone()["accepted"]

        # rejected
        query4 = """
        select count(*) as rejected
        from student_admission
        where status = 'REJECTED'
        """

        cursor.execute(query4)
        rejected_applicant = cursor.fetchone()["rejected"]

        # All Applicant
        query5 = """
        SELECT
        sa.application_id,
        sa.student_name,
        sa.email,
        d.department_name,
        sa.status
        FROM student_admission sa
        JOIN department d
        ON sa.department_id = d.department_id
        WHERE 1=1
        """

        # filter

        params = []

        if search:

            query5 += """
            and(
            cast(sa.application_id as char) like %s
            or sa.student_name like %s
            or sa.email like %s
            )
            """

            search_value = "%" + search + "%"

            params.extend([
                search_value,
                search_value,
                search_value
            ])

        if department:

            query5 += """
             and sa.department_id = %s
            """

            params.append(department)

        if status:

            query5 += """
            and sa.status = %s
            """

            params.append(status)

        if selected_date:

            query5 += """
            and date(sa.submitted_at) = %s
            """

            params.append(selected_date)

        query5 += """
        order by sa.application_id DESC
        """

        cursor.execute(query5, params)
        applications = cursor.fetchall()

        query6 = """
        select * from department order by department_name
        """

        cursor.execute(query6)
        departments = cursor.fetchall()

        return render_template("Admin/admin.html",
               total_applicant=total_applicant,
               total_pending=pending_applicant,
               total_accepted=accepted_applicant,
               total_rejected=rejected_applicant,
               applications=applications,
               departments=departments,
               search=search,
               selected_department=department,
               selected_status=status,
               selected_date=selected_date
        )

    except Error as e:

        if connection:
            connection.rollback()

        print("Database Error:", e)
        flash(f"Database Error occurred {e}", "danger")
        return(redirect(url_for("admin_dashboard")))

    finally:

        if cursor:
            cursor.close()
        if  connection:
            connection.close()

def admin_student_admission():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login_page"))

    connection = None
    cursor = None

    try:

        student_name = request.form["student_name"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        department_id = request.form["department_id"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        connection = mysql.connector.connect(
            host = MYSQL_HOST,
            user = MYSQL_USER,
            password = MYSQL_PASSWORD,
            database = MYSQL_DATABASE
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
        flash("Student admission successfully added", "success")
        return redirect(url_for("admin_dashboard"))

    except Error as e:

        if connection:
            connection.rollback()

        print("MYsql Error:", e)
        flash(f"MYSQL Error occurred {e}", "danger")
        return redirect(url_for("admin_dashboard"))

    finally:

        if cursor:
            cursor.close()
        if connection:
            connection.close()

        print("Connection closed")

# def admin_student_page():
#
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin_login_page"))
#
#     return render_template("Admin/admin_page.html")

