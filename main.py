from flask import Flask, render_template, request, redirect, url_for, session

from auth.user_auth.user import (
    student_admission,
    chatbot,
    student_login,
    student_profile
)

from config import SECRET_KEY

from auth.admin_auth.admin import (
    admin_login as process_admin_login,
    admin_dashboard as show_admin_dashboard,
    admin_student_admission as show_admin_admission,
    admin_accept_application as process_application_acceptance,
    admin_reject_application as process_application_rejection,
    admin_student_edit as show_admin_student_edit,
    admin_student_update as process_admin_student_update,
    admin_student_discontinue as process_admin_student_discontinue
)


app = Flask(__name__)
app.secret_key = SECRET_KEY

# user ui

@app.route('/')
def index():
    error = request.args.get('error')
    return render_template('user/index.html', error=error)


@app.route("/admission", methods=['POST'])
def admission():
    return student_admission()


@app.route("/chat", methods=['POST'])
def chat():
    return chatbot()


@app.route("/student-login", methods=["GET", "POST"])
def student_login_page():
    if request.method == "GET":
        return redirect(url_for("index", _anchor="login"))
    return student_login()


@app.route("/student")
def student_profile_page():
    return student_profile()


@app.route("/student-logout")
def student_logout():
    session.pop("student_logged_in", None)
    session.pop("student_id", None)
    return redirect(url_for("index", _anchor="login"))

# admin ui

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login_page():
    error = request.args.get('error')
    if request.method == "POST":
        return process_admin_login()
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
    return render_template("Admin/admin-login.html", error=error)


@app.route("/admin")
def admin_dashboard():
    return show_admin_dashboard()


@app.route("/student_admission", methods=['POST'])
def admin_student_admission_page():
        return show_admin_admission()


@app.route("/admin/applications/<int:application_id>/accept", methods=['POST'])
def admin_accept_application_page(application_id):
    return process_application_acceptance(application_id)


@app.route("/admin/applications/<int:application_id>/reject", methods=['POST'])
def admin_reject_application_page(application_id):
    return process_application_rejection(application_id)


@app.route("/admin/students/<student_id>/edit")
def admin_student_edit_page(student_id):
    return show_admin_student_edit(student_id)


@app.route("/admin/students/<student_id>/update", methods=['POST'])
def admin_student_update_page(student_id):
    return process_admin_student_update(student_id)


@app.route("/admin/students/<student_id>/discontinue", methods=['POST'])
def admin_student_discontinue_page(student_id):
    return process_admin_student_discontinue(student_id)


@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login_page"))


if __name__ == '__main__':
    app.run(debug=True)