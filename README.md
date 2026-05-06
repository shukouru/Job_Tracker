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
