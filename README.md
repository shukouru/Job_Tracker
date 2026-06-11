# 就活管理アプリ

インターンシップや就職活動の応募情報を管理するための Flask Webアプリケーションです。

このアプリでは、シンプルなWeb画面を通して、応募情報の追加・編集・検索・絞り込み・並び替え・管理ができます。データは SQLite を使ってローカルに保存されます。

## 機能

- 新しい応募情報の追加
- 既存の応募情報の編集
- 応募情報をゴミ箱へ移動
- ゴミ箱から応募情報を復元
- 応募情報を完全削除
- 会社名、職種、メモによる検索
- 応募ステータスによる絞り込み
- 締切日または会社名による並び替え
- SQLite を使ったデータ保存
- 基本的なレスポンシブCSSデザイン

## 使用技術

- Python
- Flask
- SQLite
- HTML
- CSS

## プロジェクトの目的

このプロジェクトは、Flask と SQLite を使ったバックエンドWeb開発を練習しながら、インターンシップや就職活動の応募情報を管理するための実用的なツールを作ることを目的として開発しました。

このプロジェクトを通して、以下のことを練習しました。

- Flask によるルーティングの作成
- GETリクエストとPOSTリクエストの処理
- Jinja を使ったHTMLテンプレートの表示
- SQLite を使った永続的なデータ保存
- CRUD機能の作成
- 検索、絞り込み、並び替え機能の実装
- 小規模なWebアプリケーションの構成管理

## フォルダ構成

```text
job_tracker/
├── app.py
├── static/
│   └── style.css
├── templates/
│   ├── applications.html
│   ├── add_application.html
│   ├── edit_application.html
│   └── trash.html
├── .gitignore
└── README.md

```
# Job Application Tracker

A small Flask + SQLite web app for tracking internship and job applications.

This project is intended for safe sharing with classmates and test users. Do not
commit real job-search data, personal contact details, or confidential interview
information.

## Project Background

I built this app to practice backend web development with Flask and SQLite while
creating a practical tool for organizing internship and job applications.

The next goal is to improve it collaboratively with CS-major friends, let
non-CS students test it, collect feedback, and use that feedback to make the app
clearer and easier to use.

## Features

- Add, edit, search, filter, sort, trash, restore, and permanently delete
  applications
- Track company, position, status, deadline, memo, acceptance rate, and starting
  salary
- Store application data locally with SQLite
- Responsive UI with bilingual labels for English/Japanese users
- Feedback form at `/feedback`
- Feedback is saved to a separate `feedback` table and is not displayed publicly
- Render-ready startup command with Gunicorn

## Privacy And Data Safety

- `*.db`, `.env`, virtual environments, caches, and local tool files are ignored
  by Git.
- The local SQLite database is created automatically and should stay on each
  developer's machine.
- For demos, use fake companies or non-sensitive sample data.
- This version does not include authentication, so do not publish a production
  instance containing private data.

## Tech Stack

- Python
- Flask
- SQLite
- HTML/Jinja templates
- CSS
- Gunicorn for production serving

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
│   ├── applications.html
│   ├── add_application.html
│   ├── edit_application.html
│   ├── feedback.html
│   └── trash.html
├── .gitignore
└── README.md
```

`jobs.db` is intentionally not listed because it is local data and should not be
committed.

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

3. Run the app:

```bash
python app.py
```

4. Open the app:

```text
http://localhost:5000
```

The app creates the `applications` and `feedback` tables automatically on
startup.

## Collaboration Notes

- Work on a feature branch before opening a pull request or sharing changes.
- Do not commit `jobs.db`, screenshots with personal data, or `.env` files.
- Keep UI text understandable for non-CS testers.
- Prefer small changes that preserve the current add/edit/search/trash flows.
- Test at least these paths before sharing: add application, edit application,
  move to trash, restore, delete forever, submit feedback.

## User Feedback

Test users can submit feedback from `/feedback`. The form records:

- Optional name
- User type
- Ease-of-use rating from 1 to 5
- Written comments
- Submission timestamp

To inspect feedback locally:

```bash
sqlite3 jobs.db "SELECT id, user_group, rating, comments, created_at FROM feedback;"
```

Use the comments to identify confusing labels, missing fields, and workflows
that should be simplified for non-CS students.

## Render Deployment

Render's Flask guide uses:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

This repo also includes a `Procfile` with the same Gunicorn command.

For a temporary demo, the default SQLite path (`jobs.db`) is enough, but data can
be lost when the service restarts or redeploys. For feedback that needs to
persist, attach a Render persistent disk and set:

```text
DATABASE_PATH=/var/data/jobs.db
```

Then mount the disk at `/var/data`.

References:

- Render Flask deployment docs: https://render.com/docs/deploy-flask
- Render persistent disk docs: https://render.com/docs/disks

## Future Improvements

- Add authentication before collecting real personal job-search data
- Add an admin-only feedback review page
- Add CSV export/import for applications
- Add dashboard statistics by status and deadline
- Add automated tests for routes and database setup
- Consider Postgres for a multi-user hosted version
