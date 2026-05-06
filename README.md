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

A Flask web application for managing internship and job applications.

This app allows users to add, edit, search, filter, sort, and manage job applications using a simple web interface. Data is stored locally using SQLite.

## Features

- Add new job applications
- Edit existing applications
- Move applications to trash
- Restore applications from trash
- Permanently delete applications
- Search applications by company, position, or memo
- Filter applications by status
- Sort applications by deadline or company name
- Store data using SQLite
- Basic responsive CSS styling

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS

## Project Purpose

I built this project to practice backend web development with Flask and SQLite while creating a practical tool for managing internship and job applications.

This project helped me practice:

- Building routes with Flask
- Handling GET and POST requests
- Rendering HTML templates with Jinja
- Using SQLite for persistent data storage
- Creating CRUD functionality
- Implementing search, filtering, and sorting
- Organizing a small web application project

## Folder Structure

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
