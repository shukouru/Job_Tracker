# Job Application Tracker

A Flask + SQLite web app for tracking internship and job applications.

This app is designed for safe classmate testing: each tester creates an account,
and application records are only shown to the user who created them.

## Project Background

I built this project to practice backend web development with Flask and SQLite
while creating a practical tool for managing internship and job applications.

The goal is to improve it collaboratively with CS-major friends, let non-CS
students test it, collect feedback, and use that feedback to make the app easier
to understand.

## Features

- Account registration, login, and logout
- Passwords stored with Werkzeug password hashing
- User-specific application lists, trash, edit, restore, and delete actions
- Add, edit, search, filter, and sort applications
- Track company, position, status, priority, URL, deadline, and memo
- Feedback form at `/feedback`
- Feedback is saved to a separate `feedback` table and is not displayed publicly
- Responsive UI with English/Japanese labels
- Render-ready startup command with Gunicorn

## Privacy And Data Safety

- `*.db`, `.env`, virtual environments, caches, and local tool files are ignored
  by Git.
- Do not commit `jobs.db` or any database containing real job-search data.
- Existing application rows without `user_id` are kept in the database but hidden
  from logged-in users. This prevents old local data from being exposed to a new
  tester account.
- Use fake companies or non-sensitive sample data in public demos.
- This account system is suitable for classmate testing, but a production app
  should add stronger security features such as CSRF protection, password reset,
  and admin controls.

## Tech Stack

- Python
- Flask
- SQLite
- HTML/Jinja templates
- CSS
- Gunicorn

## Folder Structure

```text
job_tracker/
├── app.py
├── requirements.txt
├── Procfile
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── applications.html
│   ├── add_application.html
│   ├── edit_application.html
│   ├── feedback.html
│   └── trash.html
├── .gitignore
└── README.md
```

## Local Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set a local session secret:

```bash
export SECRET_KEY="replace-with-a-long-random-string"
```

4. Run the app:

```bash
python app.py
```

5. Open the app:

```text
http://localhost:5000
```

The app creates the `users`, `applications`, and `feedback` tables
automatically on startup.

## Collaboration Notes

- Work on a feature branch before sharing changes.
- Do not commit `jobs.db`, screenshots with personal data, or `.env` files.
- Keep labels understandable for non-CS testers.
- Test registration, login, add application, edit application, move to trash,
  restore, delete forever, feedback submission, and logout before sharing.

## User Feedback

Logged-in test users can submit feedback from `/feedback`. The form records:

- User account ID
- Optional display name
- User type
- Ease-of-use rating from 1 to 5
- Written comments
- Submission timestamp

To inspect feedback locally:

```bash
sqlite3 jobs.db "SELECT id, user_id, user_group, rating, comments, created_at FROM feedback;"
```

Use the comments to identify confusing labels, missing fields, and workflows
that should be simplified for non-CS students.

## Render Deployment

Render's Flask guide uses:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

This repo also includes a `Procfile` with the same Gunicorn command.

Set these environment variables in Render:

```text
SECRET_KEY=<long random string>
DATABASE_PATH=/var/data/jobs.db
```

For persistent SQLite data, attach a Render persistent disk and mount it at
`/var/data`. Without a persistent disk, data can be lost on restart or redeploy.

References:

- Render Flask deployment docs: https://render.com/docs/deploy-flask
- Render persistent disk docs: https://render.com/docs/disks

## Future Improvements

- Add CSRF protection for all forms
- Add password reset or invite-only tester accounts
- Add an admin-only feedback review page
- Add CSV export/import for applications
- Add dashboard statistics by status and deadline
- Add automated tests for routes and database setup
- Consider Postgres for a more durable multi-user hosted version
