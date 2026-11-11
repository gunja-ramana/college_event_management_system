
import mysql.connector
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )

        print("MySQL connected successfully")
        return connection

    except mysql.connector.Error as e:
        print("Connection error:", e)
        return None


def create_database():
    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS college_event_db"
        )

        print("Database created successfully")

        cursor.close()
        connection.close()


def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database="college_event_db"
        )

        return connection

    except mysql.connector.Error as e:
        print("Database connection error:", e)
        return None
