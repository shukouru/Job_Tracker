from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "jobs.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            status TEXT NOT NULL,
            deadline TEXT,
            memo TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect("/applications")


@app.route("/applications")
def show_applications():
    search = request.args.get("search")
    status = request.args.get("status")
    sort = request.args.get("sort")

    conn = get_db_connection()

    query = """
        SELECT * FROM applications
        WHERE is_deleted = 0
    """

    params = []

    if search:
        query += """
            AND (
                company LIKE ?
                OR position LIKE ?
                OR memo LIKE ?
            )
        """
        params.append("%" + search + "%")
        params.append("%" + search + "%")
        params.append("%" + search + "%")

    if status:
        query += """
            AND status = ?
        """
        params.append(status)

    if sort == "deadline":
        query += """
            ORDER BY deadline ASC
        """
    elif sort == "company":
        query += """
            ORDER BY company ASC
        """
    else:
        query += """
            ORDER BY id DESC
        """

    applications = conn.execute(query, params).fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=applications,
        search=search,
        status=status,
        sort=sort
    )


@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        company = request.form.get("company")
        position = request.form.get("position")
        status = request.form.get("status")
        deadline = request.form.get("deadline")
        memo = request.form.get("memo")

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO applications (company, position, status, deadline, memo)
            VALUES (?, ?, ?, ?, ?)
        """, (company, position, status, deadline, memo))

        conn.commit()
        conn.close()

        return redirect("/applications")

    return render_template("add_application.html")


@app.route("/applications/<int:application_id>/trash", methods=["POST"])
def move_to_trash(application_id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE applications
        SET is_deleted = 1
        WHERE id = ?
    """, (application_id,))

    conn.commit()
    conn.close()

    return redirect("/applications")


@app.route("/trash")
def show_trash():
    conn = get_db_connection()

    applications = conn.execute("""
        SELECT * FROM applications
        WHERE is_deleted = 1
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("trash.html", applications=applications)


@app.route("/applications/<int:application_id>/restore", methods=["POST"])
def restore_application(application_id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE applications
        SET is_deleted = 0
        WHERE id = ?
    """, (application_id,))

    conn.commit()
    conn.close()

    return redirect("/trash")

@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    conn = get_db_connection()

    application = conn.execute("""
        SELECT * FROM applications
        WHERE id = ?
    """, (application_id,)).fetchone()

    if request.method == "POST":
        company = request.form.get("company")
        position = request.form.get("position")
        status = request.form.get("status")
        deadline = request.form.get("deadline")
        memo = request.form.get("memo")

        conn.execute("""
            UPDATE applications
            SET company = ?, position = ?, status = ?, deadline = ?, memo = ?
            WHERE id = ?
        """, (company, position, status, deadline, memo, application_id))

        conn.commit()
        conn.close()

        return redirect("/applications")

    conn.close()

    return render_template("edit_application.html", application=application)


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def delete_application(application_id):
    conn = get_db_connection()

    conn.execute("""
        DELETE FROM applications
        WHERE id = ?
    """, (application_id,))

    conn.commit()
    conn.close()

    return redirect("/trash")


if __name__ == "__main__":
    create_table()
    app.run(debug=True)