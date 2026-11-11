# College Event Management System

A Python and MySQL-based application designed to manage college events and simplify event-related activities.

## Overview

The College Event Management System helps colleges manage students, organizers, venues, events, registrations, attendance, feedback, expenses, and certificates through a centralized application.

## Technologies Used

- Python
- MySQL
- MySQL Connector
- SQL
- Python-dotenv

## Features

- Student management
- Organizer management
- Venue management
- Event management
- Student event registrations
- Attendance tracking
- Feedback management
- Event expense management
- Certificate management
- Automatic database and table creation

## Database Structure

The application uses a MySQL database named `college_event_db` with nine tables:

1. Students
2. Organizers
3. Venues
4. Events
5. Registrations
6. Attendance
7. Feedback
8. Expenses
9. Certificates

## Project Structure

```text
college_event_management_system/
│
├── main.py
├── database.py
├── .env.example
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/gunja-ramana/college_event_management_system.git
cd college_event_management_system
```

### 2. Install dependencies

```bash
pip install mysql-connector-python python-dotenv
```

### 3. Configure MySQL

Make sure MySQL Server is installed and running.

Create a `.env` file in the project folder:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
```

Replace `your_mysql_password` with your local MySQL password.

### 4. Run the application

```bash
python main.py
```

The application automatically creates the `college_event_db` database and its required tables.

## Security

Database credentials are stored in a local `.env` file and should never be uploaded to GitHub.

## Author

Ramana Gunja

## License

This project is available for educational purposes.
