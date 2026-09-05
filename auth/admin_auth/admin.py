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

    section = request.args.get("section", "application").strip()

    allowed_section = (
        "application",
        "student_admission",
        "all_student",
    )

    if section not in allowed_section:
        section = "application"

    connection = None
    cursor = None

    try:

        # applicant filter
        search = request.args.get("search", "").strip()
        department = request.args.get("department", "").strip()
        status = request.args.get("status", "").strip()
        selected_date = request.args.get("date", "").strip()

        # student detail filter
        student_search = request.args.get("student_search", "").strip()
        student_department = request.args.get("student_department", "").strip()
        student_status = request.args.get("student_status", "").strip().upper()
        student_joined_date = request.args.get("student_joined_date", "").strip()


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

        student_records, student_departments = admin_student_detail(
            cursor,
            student_search=student_search,
            student_department=student_department,
            student_status=student_status,
            student_joined_date=student_joined_date
        )

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
               selected_date=selected_date,
               student_records=student_records,
               student_departments=student_departments,
               student_search=student_search,
               selected_student_department=student_department,
               selected_student_status=student_status,
               selected_student_joined_date=student_joined_date,
               section=section
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
        return redirect(url_for("admin_dashboard", section="student_admission"))

    except Error as e:

        if connection:
            connection.rollback()

        print("MYsql Error:", e)
        flash(f"MYSQL Error occurred {e}", "danger")
        return redirect(url_for("admin_dashboard", section="student_admission"))

    finally:

        if cursor:
            cursor.close()
        if connection:
            connection.close()

        print("Connection closed")


def admin_update_application_status(application_id, new_status):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login_page"))

    connection = None
    cursor = None
    student_id_lock_acquired = False

    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = connection.cursor(dictionary=True)

        # Only pending applications may receive a final decision.
        cursor.execute("""
            SELECT sa.application_id, sa.student_name, sa.dob, sa.gender,
                   sa.department_id, sa.email, sa.phone, sa.address,
                   d.department_name
            FROM student_admission sa
            JOIN department d ON d.department_id = sa.department_id
            WHERE sa.application_id = %s AND sa.status = 'PENDING'
            FOR UPDATE
        """, (application_id,))
        application = cursor.fetchone()

        if not application:
            flash("This application is no longer pending and cannot be updated.", "warning")
            return redirect(url_for("admin_dashboard") + "#application")

        if new_status == "REJECTED":
            cursor.execute("""
                UPDATE student_admission
                SET status = 'REJECTED'
                WHERE application_id = %s AND status = 'PENDING'
            """, (application_id,))
            connection.commit()
            flash("Application rejected.", "success")
            return redirect(url_for("admin_dashboard") + "#application")

        cursor.execute("SELECT GET_LOCK('student_detail_id_generation', 10) AS acquired")
        lock_result = cursor.fetchone()
        student_id_lock_acquired = bool(lock_result and lock_result["acquired"])
        if not student_id_lock_acquired:
            raise Error("Could not obtain the student ID generation lock")

        cursor.execute("""
            SELECT student_id
            FROM student_detail
            WHERE student_id REGEXP '^scc[0-9]+$'
            ORDER BY CAST(SUBSTRING(student_id, 4) AS UNSIGNED) DESC
            LIMIT 1
            FOR UPDATE
        """)

        latest_student = cursor.fetchone()
        next_number = int(latest_student["student_id"][3:]) + 1 if latest_student else 1
        student_id = f"scc{next_number:04d}"

        cursor.execute("SELECT student_id FROM student_detail WHERE application_id = %s", (application_id,))

        if cursor.fetchone():
            raise Error("A student record already exists for this application")

        cursor.execute("""
            UPDATE student_admission
            SET status = 'ACCEPTED'
            WHERE application_id = %s AND status = 'PENDING'
        """, (application_id,))

        if cursor.rowcount != 1:
            raise Error("Application status could not be updated")

        cursor.execute("""
            INSERT INTO student_detail
            (student_id, 
            application_id, 
            student_name, 
            dob, 
            gender, 
            department_id,
            email, 
            phone, 
            address, 
            status, 
            joined_at, 
            department_name, 
            class_no)

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'CONTINUE',
                    CURRENT_TIMESTAMP, %s, %s)
        """, 
        (
            student_id,
            application["application_id"],
            application["student_name"],
            application["dob"],
            application["gender"],
            application["department_id"],
            application["email"],
            application["phone"],
            application["address"],
            application["department_name"],
            1
        ))

        cursor.execute("""
            INSERT INTO student_login
            (student_id, username, dob, student_password, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (student_id, student_id, application["dob"], application["dob"]))

        connection.commit()

        flash(f"Application accepted. Student ID: {student_id}", "success")
        return redirect(url_for("admin_dashboard") + "#application")

    except Error as e:
        if connection:
            connection.rollback()

        print("Database Error:", e)
        flash("Could not update the application. Please try again.", "danger")
        return redirect(url_for("admin_dashboard") + "#application")

    finally:
        if cursor and student_id_lock_acquired:
            try:
                cursor.execute("SELECT RELEASE_LOCK('student_detail_id_generation')")
                cursor.fetchone()
            except Error as e:
                print("Student ID lock release error:", e)

        if cursor:
            cursor.close()
        if connection:
            connection.close()


def admin_accept_application(application_id):
    return admin_update_application_status(application_id, "ACCEPTED")


def admin_reject_application(application_id):
    return admin_update_application_status(application_id, "REJECTED")


def admin_student_edit(student_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login_page"))

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
            SELECT 
            sd.student_id, 
            sd.application_id, 
            sd.student_name, 
            sd.dob,
            sd.gender, 
            sd.class_no, 
            sd.department_id, 
            sd.department_name,
            sd.email, 
            sd.phone, 
            sd.address, 
            sd.status
            FROM student_detail sd
            WHERE sd.student_id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            flash("Student record not found.", "warning")
            return redirect(url_for("admin_dashboard", section="all_student"))
        if str(student["status"]).upper() == "DISCONTINUE":
            flash("Discontinued student records cannot be edited.", "warning")
            return redirect(url_for("admin_dashboard", section="all_student"))
        return render_template("Admin/admin_page.html", student=student)
    
    except Error as e:
        print("Database Error:", e)
        flash("Could not load the student record.", "danger")
        return redirect(url_for("admin_dashboard", section="all_student"))
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def admin_student_update(student_id):
    
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login_page"))

    connection = None
    cursor = None

    try:
        student_name = request.form["student_name"].strip()
        dob = request.form["dob"]
        gender = request.form["gender"]
        class_no = request.form["class_no"].strip()
        department_id = request.form["department_id"]
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        address = request.form["address"].strip()

        connection = mysql.connector.connect(
            host=MYSQL_HOST, 
            user=MYSQL_USER, 
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT department_name FROM department WHERE department_id = %s",
            (department_id,)
        )

        department = cursor.fetchone()

        if not department:
            raise Error("Selected department does not exist")

        cursor.execute("""
            UPDATE student_detail
            SET student_name = %s, dob = %s, gender = %s, class_no = %s,
                department_id = %s, department_name = %s, email = %s,
                phone = %s, address = %s
            WHERE student_id = %s
        """, (
            student_name, dob, gender, class_no, department_id,
            department["department_name"], email, phone, address, student_id
        ))

        if cursor.rowcount != 1:
            raise Error("Student record was not updated")
        connection.commit()

        flash("Student record updated successfully.", "success")

    except (Error, KeyError) as e:
        if connection:
            connection.rollback()
        print("Database Error:", e)
        flash("Could not update the student record.", "danger")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return redirect(url_for("admin_dashboard", section="all_student"))


def admin_student_discontinue(student_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login_page"))

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST, 
            user=MYSQL_USER, 
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        cursor = connection.cursor()
        cursor.execute("""
            UPDATE student_detail
            SET status = 'DISCONTINUE'
            WHERE student_id = %s
        """, (student_id,))

        if cursor.rowcount != 1:
            raise Error("Student record was not found")
        cursor.execute(
            "DELETE FROM student_login WHERE student_id = %s",
            (student_id,)
        )
        connection.commit()
        flash("Student has been discontinued.", "success")

    except Error as e:
        if connection:
            connection.rollback()
        print("Database Error:", e)
        flash("Could not discontinue the student.", "danger")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return redirect(url_for("admin_dashboard", section="all_student"))

def admin_student_detail(cursor, student_search="", student_department="", student_status="", student_joined_date=""):

    student_query = """
        SELECT
            sd.student_id,
            sd.application_id AS app_id,
            sd.student_name,
            sd.dob,
            sd.class_no,
            sd.email,
            sd.phone,
            sd.address,
            sd.department_id,
            sd.department_name,
            CASE
                WHEN UPPER(sd.status) IN ('NEW', 'ACCEPTED') THEN 'CONTINUE'
                ELSE UPPER(sd.status)
            END AS status,
            DATE_FORMAT(sd.joined_at, '%Y-%m-%d') AS joined_date,
            DATE_FORMAT(sd.joined_at, '%d-%m-%Y') AS joined_at
        FROM student_detail sd
        WHERE 1 = 1
    """

    params = []

    if student_search:
        student_query += """
            AND (
                sd.student_id LIKE %s
                OR CAST(sd.application_id AS CHAR) LIKE %s
                OR sd.student_name LIKE %s
            )
        """
        student_search_value = f"%{student_search}%"
        params.extend([
            student_search_value,
            student_search_value,
            student_search_value
        ])

    if student_department:
        student_query += """
            AND sd.department_id = %s
        """
        params.append(student_department)

    if student_status:
        student_query += """
            AND CASE
                WHEN UPPER(sd.status) IN ('NEW', 'ACCEPTED') THEN 'CONTINUE'
                ELSE UPPER(sd.status)
            END = %s
        """
        params.append(student_status)

    if student_joined_date:
        student_query += """
            AND DATE(sd.joined_at) = %s
        """
        params.append(student_joined_date)

    student_query += """
        ORDER BY sd.joined_at DESC, sd.student_id DESC
    """

    cursor.execute(student_query, params)
    student_records = cursor.fetchall()

    cursor.execute("""
        SELECT DISTINCT
            department_id,
            department_name
        FROM student_detail
        WHERE department_name IS NOT NULL
        ORDER BY department_name
    """)
    student_departments = cursor.fetchall()

    return student_records, student_departments
