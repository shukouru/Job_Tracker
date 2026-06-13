from datetime import datetime, timezone
from functools import wraps
import os
import re
import sqlite3

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE") == "1",
)

DATABASE = os.environ.get("DATABASE_PATH", "jobs.db")
STATUSES = ["未応募", "応募済み", "面接予定", "内定", "不合格"]
PRIORITIES = ["高", "中", "低"]
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


def ensure_database_directory():
    database_dir = os.path.dirname(DATABASE)
    if database_dir:
        os.makedirs(database_dir, exist_ok=True)


def get_db_connection():
    ensure_database_directory()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def add_column_if_missing(conn, table_name, column_name, column_definition):
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {column["name"] for column in columns}

    if column_name not in existing_columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company TEXT NOT NULL,
            position TEXT,
            status TEXT NOT NULL,
            priority TEXT DEFAULT '中',
            url TEXT,
            deadline TEXT,
            memo TEXT,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    add_column_if_missing(conn, "applications", "user_id", "user_id INTEGER REFERENCES users (id)")
    add_column_if_missing(conn, "applications", "priority", "priority TEXT DEFAULT '中'")
    add_column_if_missing(conn, "applications", "url", "url TEXT")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            user_group TEXT,
            rating INTEGER,
            comments TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    add_column_if_missing(conn, "feedback", "user_id", "user_id INTEGER REFERENCES users (id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications (user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback (user_id)")

    conn.commit()
    conn.close()


def clean_form_value(field_name):
    return request.form.get(field_name, "").strip()


def application_form_data():
    return {
        "company": clean_form_value("company"),
        "position": clean_form_value("position"),
        "status": clean_form_value("status"),
        "priority": clean_form_value("priority") or "中",
        "url": clean_form_value("url"),
        "deadline": clean_form_value("deadline"),
        "memo": clean_form_value("memo"),
    }


def validate_application_form(form_data):
    if not form_data["company"]:
        return "Company is required."

    if form_data["status"] not in STATUSES:
        return "Please choose a valid status."

    if form_data["priority"] not in PRIORITIES:
        return "Please choose a valid priority."

    if form_data["url"] and not form_data["url"].startswith(("http://", "https://")):
        return "URL must start with http:// or https://."

    return None


def normalize_username(username):
    return username.strip().lower()


def validate_registration(username, password, confirm_password):
    if not USERNAME_PATTERN.fullmatch(username):
        return "Username must be 3-30 characters using letters, numbers, dot, underscore, or hyphen."

    if len(password) < 8:
        return "Password must be at least 8 characters."

    if password != confirm_password:
        return "Passwords do not match."

    return None


def safe_next_url(next_url):
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return url_for("show_applications")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None

    if user_id is None:
        return

    conn = get_db_connection()
    g.user = conn.execute("""
        SELECT id, username
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()
    conn.close()

    if g.user is None:
        session.clear()


@app.context_processor
def inject_current_user():
    return {"current_user": g.get("user")}


@app.route("/")
def home():
    if g.user is None:
        return redirect(url_for("login"))

    return redirect(url_for("show_applications"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user is not None:
        return redirect(url_for("show_applications"))

    if request.method == "POST":
        username = normalize_username(clean_form_value("username"))
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = validate_registration(username, password, confirm_password)

        if error:
            return render_template(
                "register.html",
                error=error,
                form={"username": username}
            ), 400

        conn = get_db_connection()

        try:
            cursor = conn.execute("""
                INSERT INTO users (username, password_hash, created_at)
                VALUES (?, ?, ?)
            """, (
                username,
                generate_password_hash(password),
                datetime.now(timezone.utc).isoformat(timespec="seconds")
            ))
            conn.commit()
            new_user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                "register.html",
                error="That username is already taken.",
                form={"username": username}
            ), 400

        conn.close()
        session.clear()
        session["user_id"] = new_user_id

        return redirect(url_for("show_applications"))

    return render_template("register.html", form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(url_for("show_applications"))

    next_url = request.args.get("next", "")

    if request.method == "POST":
        username = normalize_username(clean_form_value("username"))
        password = request.form.get("password", "")
        next_url = request.form.get("next", "")

        conn = get_db_connection()
        user = conn.execute("""
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html",
                error="Incorrect username or password.",
                form={"username": username},
                next_url=next_url
            ), 400

        session.clear()
        session["user_id"] = user["id"]

        return redirect(safe_next_url(next_url))

    return render_template("login.html", form={}, next_url=next_url)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/applications")
@login_required
def show_applications():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    sort = request.args.get("sort")

    if status not in STATUSES:
        status = ""

    if priority not in PRIORITIES:
        priority = ""

    conn = get_db_connection()

    query = """
        SELECT * FROM applications
        WHERE is_deleted = 0
        AND user_id = ?
    """

    params = [g.user["id"]]

    if search:
        query += """
            AND (
                company LIKE ?
                OR position LIKE ?
                OR url LIKE ?
                OR memo LIKE ?
                OR priority LIKE ?
            )
        """
        search_term = "%" + search + "%"
        params.extend([search_term, search_term, search_term, search_term, search_term])

    if status:
        query += """
            AND status = ?
        """
        params.append(status)

    if priority:
        query += """
            AND priority = ?
        """
        params.append(priority)

    if sort == "deadline":
        query += """
            ORDER BY deadline ASC
        """
    elif sort == "company":
        query += """
            ORDER BY company ASC
        """
    elif sort == "priority":
        query += """
            ORDER BY
                CASE priority
                    WHEN '高' THEN 1
                    WHEN '中' THEN 2
                    WHEN '低' THEN 3
                    ELSE 4
                END,
                deadline ASC,
                id DESC
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
        priority=priority,
        sort=sort,
        statuses=STATUSES,
        priorities=PRIORITIES
    )


@app.route("/applications/add", methods=["GET", "POST"])
@login_required
def add_application():
    if request.method == "POST":
        form_data = application_form_data()
        error = validate_application_form(form_data)

        if error:
            return render_template(
                "add_application.html",
                error=error,
                form=form_data,
                statuses=STATUSES,
                priorities=PRIORITIES
            ), 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO applications (
                company,
                user_id,
                position,
                status,
                priority,
                url,
                deadline,
                memo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            form_data["company"],
            g.user["id"],
            form_data["position"],
            form_data["status"],
            form_data["priority"],
            form_data["url"],
            form_data["deadline"],
            form_data["memo"]
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("show_applications"))

    return render_template(
        "add_application.html",
        form={},
        statuses=STATUSES,
        priorities=PRIORITIES
    )


@app.route("/applications/<int:application_id>/trash", methods=["POST"])
@login_required
def move_to_trash(application_id):
    conn = get_db_connection()

    cursor = conn.execute("""
        UPDATE applications
        SET is_deleted = 1
        WHERE id = ?
        AND user_id = ?
    """, (application_id, g.user["id"]))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        abort(404)

    return redirect(url_for("show_applications"))


@app.route("/trash")
@login_required
def show_trash():
    conn = get_db_connection()

    applications = conn.execute("""
        SELECT * FROM applications
        WHERE is_deleted = 1
        AND user_id = ?
        ORDER BY id DESC
    """, (g.user["id"],)).fetchall()

    conn.close()

    return render_template("trash.html", applications=applications)


@app.route("/applications/<int:application_id>/restore", methods=["POST"])
@login_required
def restore_application(application_id):
    conn = get_db_connection()

    cursor = conn.execute("""
        UPDATE applications
        SET is_deleted = 0
        WHERE id = ?
        AND user_id = ?
    """, (application_id, g.user["id"]))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        abort(404)

    return redirect(url_for("show_trash"))


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
@login_required
def edit_application(application_id):
    conn = get_db_connection()
    next_url = safe_next_url(request.values.get("next", ""))

    application = conn.execute("""
        SELECT * FROM applications
        WHERE id = ?
        AND user_id = ?
    """, (application_id, g.user["id"])).fetchone()

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
                statuses=STATUSES,
                priorities=PRIORITIES,
                next_url=next_url
            ), 400

        conn.execute("""
            UPDATE applications
            SET company = ?, position = ?, status = ?, priority = ?, url = ?, deadline = ?, memo = ?
            WHERE id = ?
            AND user_id = ?
        """, (
            form_data["company"],
            form_data["position"],
            form_data["status"],
            form_data["priority"],
            form_data["url"],
            form_data["deadline"],
            form_data["memo"],
            application_id,
            g.user["id"]
        ))

        conn.commit()
        conn.close()

        return redirect(next_url)

    conn.close()

    return render_template(
        "edit_application.html",
        application=application,
        form=dict(application),
        statuses=STATUSES,
        priorities=PRIORITIES,
        next_url=next_url
    )


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
@login_required
def delete_application(application_id):
    conn = get_db_connection()

    cursor = conn.execute("""
        DELETE FROM applications
        WHERE id = ?
        AND user_id = ?
    """, (application_id, g.user["id"]))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        abort(404)

    return redirect(url_for("show_trash"))


@app.route("/feedback", methods=["GET", "POST"])
@login_required
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
            INSERT INTO feedback (user_id, name, user_group, rating, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            g.user["id"],
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
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
