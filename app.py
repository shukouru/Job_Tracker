from datetime import datetime, timezone
import os
import sqlite3

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

DATABASE = os.environ.get("DATABASE_PATH", "jobs.db")
STATUSES = ["未応募", "応募済み", "面接予定", "内定", "不合格"]


def ensure_database_directory():
    database_dir = os.path.dirname(DATABASE)
    if database_dir:
        os.makedirs(database_dir, exist_ok=True)


def get_db_connection():
    ensure_database_directory()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def add_column_if_missing(conn, table_name, column_name, column_definition):
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {column["name"] for column in columns}

    if column_name not in existing_columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            status TEXT NOT NULL,
            deadline TEXT,
            memo TEXT,
            acceptance_rate TEXT,
            starting_salary TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    """)

    add_column_if_missing(conn, "applications", "acceptance_rate", "acceptance_rate TEXT")
    add_column_if_missing(conn, "applications", "starting_salary", "starting_salary TEXT")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            user_group TEXT,
            rating INTEGER,
            comments TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def clean_form_value(field_name):
    return request.form.get(field_name, "").strip()


def application_form_data():
    return {
        "company": clean_form_value("company"),
        "position": clean_form_value("position"),
        "status": clean_form_value("status"),
        "deadline": clean_form_value("deadline"),
        "memo": clean_form_value("memo"),
        "acceptance_rate": clean_form_value("acceptance_rate"),
        "starting_salary": clean_form_value("starting_salary"),
    }


def validate_application_form(form_data):
    if not form_data["company"] or not form_data["position"]:
        return "Company and position are required."

    if form_data["status"] not in STATUSES:
        return "Please choose a valid status."

    return None


@app.route("/")
def home():
    return redirect(url_for("show_applications"))


@app.route("/applications")
def show_applications():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    sort = request.args.get("sort")

    if status not in STATUSES:
        status = ""

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
                OR acceptance_rate LIKE ?
                OR starting_salary LIKE ?
            )
        """
        search_term = "%" + search + "%"
        params.extend([search_term, search_term, search_term, search_term, search_term])

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
        sort=sort,
        statuses=STATUSES
    )


@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        form_data = application_form_data()
        error = validate_application_form(form_data)

        if error:
            return render_template(
                "add_application.html",
                error=error,
                form=form_data,
                statuses=STATUSES
            ), 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO applications (
                company,
                position,
                status,
                deadline,
                memo,
                acceptance_rate,
                starting_salary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            form_data["company"],
            form_data["position"],
            form_data["status"],
            form_data["deadline"],
            form_data["memo"],
            form_data["acceptance_rate"],
            form_data["starting_salary"]
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("show_applications"))

    return render_template("add_application.html", form={}, statuses=STATUSES)


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

    return redirect(url_for("show_applications"))


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

    return redirect(url_for("show_trash"))


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    conn = get_db_connection()

    application = conn.execute("""
        SELECT * FROM applications
        WHERE id = ?
    """, (application_id,)).fetchone()

    if application is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        form_data = application_form_data()
        error = validate_application_form(form_data)

        if error:
            conn.close()
            return render_template(
                "edit_application.html",
                application=application,
                error=error,
                form=form_data,
                statuses=STATUSES
            ), 400

        conn.execute("""
            UPDATE applications
            SET company = ?, position = ?, status = ?, deadline = ?, memo = ?, acceptance_rate = ?, starting_salary = ?
            WHERE id = ?
        """, (
            form_data["company"],
            form_data["position"],
            form_data["status"],
            form_data["deadline"],
            form_data["memo"],
            form_data["acceptance_rate"],
            form_data["starting_salary"],
            application_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("show_applications"))

    conn.close()

    return render_template(
        "edit_application.html",
        application=application,
        form=dict(application),
        statuses=STATUSES
    )


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def delete_application(application_id):
    conn = get_db_connection()

    conn.execute("""
        DELETE FROM applications
        WHERE id = ?
    """, (application_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("show_trash"))


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        form_data = {
            "name": clean_form_value("name"),
            "user_group": clean_form_value("user_group"),
            "rating": clean_form_value("rating"),
            "comments": clean_form_value("comments"),
        }

        error = None
        rating = None

        if form_data["rating"]:
            try:
                rating = int(form_data["rating"])
            except ValueError:
                error = "Please choose a valid rating."

        if rating is not None and rating not in range(1, 6):
            error = "Please choose a rating from 1 to 5."

        if not form_data["comments"]:
            error = "Please write at least one comment."

        if error:
            return render_template(
                "feedback.html",
                error=error,
                form=form_data,
                submitted=False
            ), 400

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO feedback (name, user_group, rating, comments, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            form_data["name"],
            form_data["user_group"],
            rating,
            form_data["comments"],
            datetime.now(timezone.utc).isoformat(timespec="seconds")
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("feedback", submitted="1"))

    return render_template(
        "feedback.html",
        form={},
        submitted=request.args.get("submitted") == "1"
    )


init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
