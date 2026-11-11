import mysql.connector
from datetime import date

from database import create_database, get_database_connection


# ============================================================
# INPUT VALIDATION FUNCTIONS
# ============================================================

def get_integer(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid amount.")


def get_rating(prompt):
    while True:
        try:
            rating = int(input(prompt))

            if 1 <= rating <= 5:
                return rating

            print("Rating must be between 1 and 5.")

        except ValueError:
            print("Invalid input. Please enter a number from 1 to 5.")


def get_date(prompt):
    while True:
        date_value = input(prompt)

        try:
            date.fromisoformat(date_value)
            return date_value

        except ValueError:
            print("Invalid date format.")
            print("Please enter date as YYYY-MM-DD.")


def get_attendance_status():
    while True:
        status = input("Enter Attendance Status (Present/Absent): ").strip().title()

        if status in ["Present", "Absent"]:
            return status

        print("Invalid status. Please enter Present or Absent.")


def get_certificate_type():
    while True:
        certificate_type = input(
            "Enter Certificate Type (Winner/Runner-up/Participation): "
        ).strip()

        if certificate_type in ["Winner", "Runner-up", "Participation"]:
            return certificate_type

        print("Invalid certificate type.")


def get_certificate_status():
    while True:
        status = input(
            "Enter Certificate Status (Issued/Pending): "
        ).strip().title()

        if status in ["Issued", "Pending"]:
            return status

        print("Invalid status. Please enter Issued or Pending.")


# ============================================================
# DATABASE ERROR HANDLER
# ============================================================

def handle_database_error(e):

    if e.errno == 1062:
        print("Error: This record already exists.")

    elif e.errno == 1451:
        print("Error: This record cannot be deleted.")
        print("It is being used by another record.")

    elif e.errno == 1452:
        print("Error: Related record does not exist.")
        print("Please check the ID you entered.")

    elif e.errno == 1054:
        print("Error: Database column or field does not exist.")

    elif e.errno == 1146:
        print("Error: Database table does not exist.")

    else:
        print("Database Error:", e)


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            # ------------------------------------------------
            # 1. STUDENTS
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    phone VARCHAR(15),
                    department VARCHAR(50),
                    year INT
                )
            """)

            # ------------------------------------------------
            # 2. ORGANIZERS
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS organizers (
                    organizer_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    role VARCHAR(50),
                    email VARCHAR(100),
                    phone VARCHAR(15),
                    department VARCHAR(50)
                )
            """)

            # ------------------------------------------------
            # 3. VENUES
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS venues (
                    venue_id VARCHAR(20) PRIMARY KEY,
                    venue_name VARCHAR(100) NOT NULL,
                    location VARCHAR(150),
                    capacity INT
                )
            """)

            # ------------------------------------------------
            # 4. EVENTS
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id VARCHAR(20) PRIMARY KEY,
                    event_name VARCHAR(100) NOT NULL,
                    event_date DATE,
                    description TEXT,
                    organizer_id VARCHAR(20),
                    venue_id VARCHAR(20),

                    FOREIGN KEY (organizer_id)
                        REFERENCES organizers(organizer_id),

                    FOREIGN KEY (venue_id)
                        REFERENCES venues(venue_id)
                )
            """)

            # ------------------------------------------------
            # 5. REGISTRATIONS
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    registration_id VARCHAR(20) PRIMARY KEY,
                    student_id VARCHAR(20),
                    event_id VARCHAR(20),
                    registration_date DATE,

                    FOREIGN KEY (student_id)
                        REFERENCES students(student_id),

                    FOREIGN KEY (event_id)
                        REFERENCES events(event_id),

                    UNIQUE (student_id, event_id)
                )
            """)

            # ------------------------------------------------
            # 6. ATTENDANCE
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    registration_id VARCHAR(20) PRIMARY KEY,
                    status VARCHAR(20),

                    FOREIGN KEY (registration_id)
                        REFERENCES registrations(registration_id)
                )
            """)

            # ------------------------------------------------
            # 7. FEEDBACK
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    registration_id VARCHAR(20) PRIMARY KEY,
                    rating INT,
                    comments VARCHAR(255),

                    FOREIGN KEY (registration_id)
                        REFERENCES registrations(registration_id)
                )
            """)

            # ------------------------------------------------
            # 8. EXPENSES
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    event_id VARCHAR(20) PRIMARY KEY,
                    expense_type VARCHAR(100),
                    amount DECIMAL(10,2),
                    expense_date DATE,

                    FOREIGN KEY (event_id)
                        REFERENCES events(event_id)
                )
            """)

            # ------------------------------------------------
            # 9. CERTIFICATES
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    certificate_id VARCHAR(20) PRIMARY KEY,
                    registration_id VARCHAR(20),
                    certificate_type VARCHAR(50),
                    issue_date DATE,
                    status VARCHAR(20),

                    FOREIGN KEY (registration_id)
                        REFERENCES registrations(registration_id),

                    UNIQUE (registration_id)
                )
            """)

            connection.commit()

            print("All tables created successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# STUDENT MANAGEMENT
# ============================================================

def add_student():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        student_id = input("Enter Student ID: ")
        name = input("Enter Student Name: ")
        email = input("Enter Email: ")
        phone = input("Enter Phone: ")
        department = input("Enter Department: ")
        year = get_integer("Enter Year: ")

        query = """
            INSERT INTO students
            (student_id, name, email, phone, department, year)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            student_id,
            name,
            email,
            phone,
            department,
            year
        )

        try:
            cursor.execute(query, values)
            connection.commit()

            print("Student added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_students():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        query = """
            SELECT
                student_id,
                name,
                email,
                phone,
                department,
                year
            FROM students
        """

        try:

            cursor.execute(query)
            records = cursor.fetchall()

            if records:

                print("\n================ STUDENTS ================")

                for record in records:

                    print("----------------------------------------")
                    print("Student ID   :", record[0])
                    print("Name         :", record[1])
                    print("Email        :", record[2])
                    print("Phone        :", record[3])
                    print("Department   :", record[4])
                    print("Year         :", record[5])

                print("----------------------------------------")

            else:
                print("No student records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_student():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        student_id = input("Enter Student ID to search: ")

        query = """
            SELECT
                student_id,
                name,
                email,
                phone,
                department,
                year
            FROM students
            WHERE student_id = %s
        """

        try:

            cursor.execute(query, (student_id,))
            record = cursor.fetchone()

            if record:

                print("\n========== STUDENT DETAILS ==========")
                print("Student ID   :", record[0])
                print("Name         :", record[1])
                print("Email        :", record[2])
                print("Phone        :", record[3])
                print("Department   :", record[4])
                print("Year         :", record[5])

            else:
                print("Student not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_student():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        student_id = input("Enter Student ID to update: ")

        check_query = """
            SELECT student_id
            FROM students
            WHERE student_id = %s
        """

        try:

            cursor.execute(check_query, (student_id,))
            record = cursor.fetchone()

            if not record:
                print("Student not found.")
                cursor.close()
                connection.close()
                return

            print("\nEnter new student details:")

            name = input("Enter Name: ")
            email = input("Enter Email: ")
            phone = input("Enter Phone: ")
            department = input("Enter Department: ")
            year = get_integer("Enter Year: ")

            query = """
                UPDATE students
                SET
                    name = %s,
                    email = %s,
                    phone = %s,
                    department = %s,
                    year = %s
                WHERE student_id = %s
            """

            values = (
                name,
                email,
                phone,
                department,
                year,
                student_id
            )

            cursor.execute(query, values)
            connection.commit()

            print("Student updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_student():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        student_id = input("Enter Student ID to delete: ")

        query = """
            DELETE FROM students
            WHERE student_id = %s
        """

        try:

            cursor.execute(query, (student_id,))
            connection.commit()

            if cursor.rowcount > 0:
                print("Student deleted successfully.")
            else:
                print("Student not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def student_management():

    while True:

        print("\n========================================")
        print("          STUDENT MANAGEMENT")
        print("========================================")
        print("1. Add Student")
        print("2. View Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_student()

        elif choice == "2":
            view_students()

        elif choice == "3":
            search_student()

        elif choice == "4":
            update_student()

        elif choice == "5":
            delete_student()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# ORGANIZER MANAGEMENT
# ============================================================

def add_organizer():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        organizer_id = input("Enter Organizer ID: ")
        name = input("Enter Organizer Name: ")
        role = input("Enter Role: ")
        email = input("Enter Email: ")
        phone = input("Enter Phone: ")
        department = input("Enter Department: ")

        query = """
            INSERT INTO organizers
            (organizer_id, name, role, email, phone, department)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            organizer_id,
            name,
            role,
            email,
            phone,
            department
        )

        try:

            cursor.execute(query, values)
            connection.commit()

            print("Organizer added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_organizers():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        query = """
            SELECT
                organizer_id,
                name,
                role,
                email,
                phone,
                department
            FROM organizers
        """

        try:

            cursor.execute(query)
            records = cursor.fetchall()

            if records:

                print("\n================ ORGANIZERS ================")

                for record in records:

                    print("----------------------------------------")
                    print("Organizer ID :", record[0])
                    print("Name         :", record[1])
                    print("Role         :", record[2])
                    print("Email        :", record[3])
                    print("Phone        :", record[4])
                    print("Department   :", record[5])

            else:
                print("No organizer records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_organizer():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        organizer_id = input("Enter Organizer ID to search: ")

        query = """
            SELECT
                organizer_id,
                name,
                role,
                email,
                phone,
                department
            FROM organizers
            WHERE organizer_id = %s
        """

        try:

            cursor.execute(query, (organizer_id,))
            record = cursor.fetchone()

            if record:

                print("\n========== ORGANIZER DETAILS ==========")
                print("Organizer ID :", record[0])
                print("Name         :", record[1])
                print("Role         :", record[2])
                print("Email        :", record[3])
                print("Phone        :", record[4])
                print("Department   :", record[5])

            else:
                print("Organizer not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_organizer():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        organizer_id = input("Enter Organizer ID to update: ")

        try:

            cursor.execute(
                "SELECT organizer_id FROM organizers WHERE organizer_id = %s",
                (organizer_id,)
            )

            record = cursor.fetchone()

            if not record:
                print("Organizer not found.")
                cursor.close()
                connection.close()
                return

            name = input("Enter Name: ")
            role = input("Enter Role: ")
            email = input("Enter Email: ")
            phone = input("Enter Phone: ")
            department = input("Enter Department: ")

            query = """
                UPDATE organizers
                SET
                    name = %s,
                    role = %s,
                    email = %s,
                    phone = %s,
                    department = %s
                WHERE organizer_id = %s
            """

            values = (
                name,
                role,
                email,
                phone,
                department,
                organizer_id
            )

            cursor.execute(query, values)
            connection.commit()

            print("Organizer updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_organizer():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        organizer_id = input("Enter Organizer ID to delete: ")

        try:

            cursor.execute(
                "DELETE FROM organizers WHERE organizer_id = %s",
                (organizer_id,)
            )

            connection.commit()

            if cursor.rowcount > 0:
                print("Organizer deleted successfully.")
            else:
                print("Organizer not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def organizer_management():

    while True:

        print("\n========================================")
        print("         ORGANIZER MANAGEMENT")
        print("========================================")
        print("1. Add Organizer")
        print("2. View Organizers")
        print("3. Search Organizer")
        print("4. Update Organizer")
        print("5. Delete Organizer")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_organizer()

        elif choice == "2":
            view_organizers()

        elif choice == "3":
            search_organizer()

        elif choice == "4":
            update_organizer()

        elif choice == "5":
            delete_organizer()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# VENUE MANAGEMENT
# ============================================================

def add_venue():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        venue_id = input("Enter Venue ID: ")
        venue_name = input("Enter Venue Name: ")
        location = input("Enter Location: ")
        capacity = get_integer("Enter Capacity: ")

        query = """
            INSERT INTO venues
            (venue_id, venue_name, location, capacity)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            venue_id,
            venue_name,
            location,
            capacity
        )

        try:

            cursor.execute(query, values)
            connection.commit()

            print("Venue added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_venues():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    venue_id,
                    venue_name,
                    location,
                    capacity
                FROM venues
            """)

            records = cursor.fetchall()

            if records:

                print("\n================ VENUES ================")

                for record in records:

                    print("----------------------------------------")
                    print("Venue ID     :", record[0])
                    print("Venue Name   :", record[1])
                    print("Location     :", record[2])
                    print("Capacity     :", record[3])

            else:
                print("No venue records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_venue():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        venue_id = input("Enter Venue ID to search: ")

        try:

            cursor.execute("""
                SELECT
                    venue_id,
                    venue_name,
                    location,
                    capacity
                FROM venues
                WHERE venue_id = %s
            """, (venue_id,))

            record = cursor.fetchone()

            if record:

                print("\n========== VENUE DETAILS ==========")
                print("Venue ID     :", record[0])
                print("Venue Name   :", record[1])
                print("Location     :", record[2])
                print("Capacity     :", record[3])

            else:
                print("Venue not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_venue():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        venue_id = input("Enter Venue ID to update: ")

        try:

            cursor.execute(
                "SELECT venue_id FROM venues WHERE venue_id = %s",
                (venue_id,)
            )

            record = cursor.fetchone()

            if not record:
                print("Venue not found.")
                cursor.close()
                connection.close()
                return

            venue_name = input("Enter Venue Name: ")
            location = input("Enter Location: ")
            capacity = get_integer("Enter Capacity: ")

            query = """
                UPDATE venues
                SET
                    venue_name = %s,
                    location = %s,
                    capacity = %s
                WHERE venue_id = %s
            """

            cursor.execute(
                query,
                (venue_name, location, capacity, venue_id)
            )

            connection.commit()

            print("Venue updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_venue():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        venue_id = input("Enter Venue ID to delete: ")

        try:

            cursor.execute(
                "DELETE FROM venues WHERE venue_id = %s",
                (venue_id,)
            )

            connection.commit()

            if cursor.rowcount > 0:
                print("Venue deleted successfully.")
            else:
                print("Venue not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def venue_management():

    while True:

        print("\n========================================")
        print("           VENUE MANAGEMENT")
        print("========================================")
        print("1. Add Venue")
        print("2. View Venues")
        print("3. Search Venue")
        print("4. Update Venue")
        print("5. Delete Venue")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_venue()

        elif choice == "2":
            view_venues()

        elif choice == "3":
            search_venue()

        elif choice == "4":
            update_venue()

        elif choice == "5":
            delete_venue()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# EVENT MANAGEMENT
# ============================================================

def add_event():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID: ")
        event_name = input("Enter Event Name: ")
        event_date = get_date("Enter Event Date (YYYY-MM-DD): ")
        description = input("Enter Description: ")
        organizer_id = input("Enter Organizer ID: ")
        venue_id = input("Enter Venue ID: ")

        query = """
            INSERT INTO events
            (event_id, event_name, event_date, description, organizer_id, venue_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            event_id,
            event_name,
            event_date,
            description,
            organizer_id,
            venue_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

            print("Event added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_events():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        query = """
            SELECT
                event_id,
                event_name,
                event_date,
                description,
                organizer_id,
                venue_id
            FROM events
        """

        try:

            cursor.execute(query)
            records = cursor.fetchall()

            if records:

                print("\n================ EVENTS ================")

                for record in records:

                    print("----------------------------------------")
                    print("Event ID     :", record[0])
                    print("Event Name   :", record[1])
                    print("Event Date   :", record[2])
                    print("Description  :", record[3])
                    print("Organizer ID :", record[4])
                    print("Venue ID     :", record[5])

            else:
                print("No event records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_event():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID to search: ")

        try:

            cursor.execute("""
                SELECT
                    event_id,
                    event_name,
                    event_date,
                    description,
                    organizer_id,
                    venue_id
                FROM events
                WHERE event_id = %s
            """, (event_id,))

            record = cursor.fetchone()

            if record:

                print("\n========== EVENT DETAILS ==========")
                print("Event ID     :", record[0])
                print("Event Name   :", record[1])
                print("Event Date   :", record[2])
                print("Description  :", record[3])
                print("Organizer ID :", record[4])
                print("Venue ID     :", record[5])

            else:
                print("Event not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_event():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID to update: ")

        try:

            cursor.execute(
                "SELECT event_id FROM events WHERE event_id = %s",
                (event_id,)
            )

            record = cursor.fetchone()

            if not record:
                print("Event not found.")
                cursor.close()
                connection.close()
                return

            event_name = input("Enter Event Name: ")
            event_date = get_date("Enter Event Date (YYYY-MM-DD): ")
            description = input("Enter Description: ")
            organizer_id = input("Enter Organizer ID: ")
            venue_id = input("Enter Venue ID: ")

            query = """
                UPDATE events
                SET
                    event_name = %s,
                    event_date = %s,
                    description = %s,
                    organizer_id = %s,
                    venue_id = %s
                WHERE event_id = %s
            """

            values = (
                event_name,
                event_date,
                description,
                organizer_id,
                venue_id,
                event_id
            )

            cursor.execute(query, values)
            connection.commit()

            print("Event updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_event():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID to delete: ")

        try:

            cursor.execute(
                "DELETE FROM events WHERE event_id = %s",
                (event_id,)
            )

            connection.commit()

            if cursor.rowcount > 0:
                print("Event deleted successfully.")
            else:
                print("Event not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def event_management():

    while True:

        print("\n========================================")
        print("           EVENT MANAGEMENT")
        print("========================================")
        print("1. Add Event")
        print("2. View Events")
        print("3. Search Event")
        print("4. Update Event")
        print("5. Delete Event")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_event()

        elif choice == "2":
            view_events()

        elif choice == "3":
            search_event()

        elif choice == "4":
            update_event()

        elif choice == "5":
            delete_event()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# REGISTRATION MANAGEMENT
# ============================================================

def add_registration():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input("Enter Registration ID: ")
        student_id = input("Enter Student ID: ")
        event_id = input("Enter Event ID: ")
        registration_date = get_date(
            "Enter Registration Date (YYYY-MM-DD): "
        )

        query = """
            INSERT INTO registrations
            (registration_id, student_id, event_id, registration_date)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            registration_id,
            student_id,
            event_id,
            registration_date
        )

        try:

            cursor.execute(query, values)
            connection.commit()

            print("Registration added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_registrations():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    registration_id,
                    student_id,
                    event_id,
                    registration_date
                FROM registrations
            """)

            records = cursor.fetchall()

            if records:

                print("\n================ REGISTRATIONS ================")

                for record in records:

                    print("----------------------------------------")
                    print("Registration ID :", record[0])
                    print("Student ID      :", record[1])
                    print("Event ID        :", record[2])
                    print("Registration Date:", record[3])

            else:
                print("No registration records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_registration():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to search: "
        )

        try:

            cursor.execute("""
                SELECT
                    registration_id,
                    student_id,
                    event_id,
                    registration_date
                FROM registrations
                WHERE registration_id = %s
            """, (registration_id,))

            record = cursor.fetchone()

            if record:

                print("\n========== REGISTRATION DETAILS ==========")
                print("Registration ID :", record[0])
                print("Student ID      :", record[1])
                print("Event ID        :", record[2])
                print("Registration Date:", record[3])

            else:
                print("Registration not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_registration():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to update: "
        )

        try:

            cursor.execute("""
                SELECT registration_id
                FROM registrations
                WHERE registration_id = %s
            """, (registration_id,))

            record = cursor.fetchone()

            if not record:
                print("Registration not found.")
                cursor.close()
                connection.close()
                return

            student_id = input("Enter Student ID: ")
            event_id = input("Enter Event ID: ")

            registration_date = get_date(
                "Enter Registration Date (YYYY-MM-DD): "
            )

            query = """
                UPDATE registrations
                SET
                    student_id = %s,
                    event_id = %s,
                    registration_date = %s
                WHERE registration_id = %s
            """

            values = (
                student_id,
                event_id,
                registration_date,
                registration_id
            )

            cursor.execute(query, values)
            connection.commit()

            print("Registration updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_registration():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to delete: "
        )

        try:

            cursor.execute("""
                DELETE FROM registrations
                WHERE registration_id = %s
            """, (registration_id,))

            connection.commit()

            if cursor.rowcount > 0:
                print("Registration deleted successfully.")
            else:
                print("Registration not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def registration_management():

    while True:

        print("\n========================================")
        print("       REGISTRATION MANAGEMENT")
        print("========================================")
        print("1. Add Registration")
        print("2. View Registrations")
        print("3. Search Registration")
        print("4. Update Registration")
        print("5. Delete Registration")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_registration()

        elif choice == "2":
            view_registrations()

        elif choice == "3":
            search_registration()

        elif choice == "4":
            update_registration()

        elif choice == "5":
            delete_registration()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# ATTENDANCE MANAGEMENT
# ============================================================

def add_attendance():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input("Enter Registration ID: ")
        status = get_attendance_status()

        query = """
            INSERT INTO attendance
            (registration_id, status)
            VALUES (%s, %s)
        """

        try:

            cursor.execute(
                query,
                (registration_id, status)
            )

            connection.commit()

            print("Attendance added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_attendance():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    registration_id,
                    status
                FROM attendance
            """)

            records = cursor.fetchall()

            if records:

                print("\n================ ATTENDANCE ================")

                for record in records:

                    print("----------------------------------------")
                    print("Registration ID :", record[0])
                    print("Status          :", record[1])

            else:
                print("No attendance records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_attendance():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to search: "
        )

        try:

            cursor.execute("""
                SELECT
                    registration_id,
                    status
                FROM attendance
                WHERE registration_id = %s
            """, (registration_id,))

            record = cursor.fetchone()

            if record:

                print("\n========== ATTENDANCE DETAILS ==========")
                print("Registration ID :", record[0])
                print("Status          :", record[1])

            else:
                print("Attendance record not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_attendance():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to update attendance: "
        )

        try:

            cursor.execute("""
                SELECT registration_id
                FROM attendance
                WHERE registration_id = %s
            """, (registration_id,))

            record = cursor.fetchone()

            if not record:
                print("Attendance record not found.")
                cursor.close()
                connection.close()
                return

            status = get_attendance_status()

            cursor.execute("""
                UPDATE attendance
                SET status = %s
                WHERE registration_id = %s
            """, (status, registration_id))

            connection.commit()

            print("Attendance updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_attendance():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to delete attendance: "
        )

        try:

            cursor.execute("""
                DELETE FROM attendance
                WHERE registration_id = %s
            """, (registration_id,))

            connection.commit()

            if cursor.rowcount > 0:
                print("Attendance deleted successfully.")
            else:
                print("Attendance record not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def attendance_management():

    while True:

        print("\n========================================")
        print("        ATTENDANCE MANAGEMENT")
        print("========================================")
        print("1. Add Attendance")
        print("2. View Attendance")
        print("3. Search Attendance")
        print("4. Update Attendance")
        print("5. Delete Attendance")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_attendance()

        elif choice == "2":
            view_attendance()

        elif choice == "3":
            search_attendance()

        elif choice == "4":
            update_attendance()

        elif choice == "5":
            delete_attendance()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# FEEDBACK MANAGEMENT
# ============================================================

def add_feedback():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input("Enter Registration ID: ")
        rating = get_rating("Enter Rating (1-5): ")
        comments = input("Enter Comments: ")

        query = """
            INSERT INTO feedback
            (registration_id, rating, comments)
            VALUES (%s, %s, %s)
        """

        try:

            cursor.execute(
                query,
                (registration_id, rating, comments)
            )

            connection.commit()

            print("Feedback added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_feedback():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    registration_id,
                    rating,
                    comments
                FROM feedback
            """)

            records = cursor.fetchall()

            if records:

                print("\n================ FEEDBACK ================")

                for record in records:

                    print("----------------------------------------")
                    print("Registration ID :", record[0])
                    print("Rating          :", record[1])
                    print("Comments        :", record[2])

            else:
                print("No feedback records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_feedback():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to search feedback: "
        )

        try:

            cursor.execute("""
                SELECT
                    registration_id,
                    rating,
                    comments
                FROM feedback
                WHERE registration_id = %s
            """, (registration_id,))

            record = cursor.fetchone()

            if record:

                print("\n========== FEEDBACK DETAILS ==========")
                print("Registration ID :", record[0])
                print("Rating          :", record[1])
                print("Comments        :", record[2])

            else:
                print("Feedback record not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_feedback():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to update feedback: "
        )

        try:

            cursor.execute("""
                SELECT registration_id
                FROM feedback
                WHERE registration_id = %s
            """, (registration_id,))

            record = cursor.fetchone()

            if not record:
                print("Feedback record not found.")
                cursor.close()
                connection.close()
                return

            rating = get_rating("Enter Rating (1-5): ")
            comments = input("Enter Comments: ")

            cursor.execute("""
                UPDATE feedback
                SET
                    rating = %s,
                    comments = %s
                WHERE registration_id = %s
            """, (rating, comments, registration_id))

            connection.commit()

            print("Feedback updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_feedback():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        registration_id = input(
            "Enter Registration ID to delete feedback: "
        )

        try:

            cursor.execute("""
                DELETE FROM feedback
                WHERE registration_id = %s
            """, (registration_id,))

            connection.commit()

            if cursor.rowcount > 0:
                print("Feedback deleted successfully.")
            else:
                print("Feedback record not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def feedback_management():

    while True:

        print("\n========================================")
        print("         FEEDBACK MANAGEMENT")
        print("========================================")
        print("1. Add Feedback")
        print("2. View Feedback")
        print("3. Search Feedback")
        print("4. Update Feedback")
        print("5. Delete Feedback")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_feedback()

        elif choice == "2":
            view_feedback()

        elif choice == "3":
            search_feedback()

        elif choice == "4":
            update_feedback()

        elif choice == "5":
            delete_feedback()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# CERTIFICATE MANAGEMENT
# ============================================================

def add_certificate():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        certificate_id = input("Enter Certificate ID: ")
        registration_id = input("Enter Registration ID: ")
        certificate_type = get_certificate_type()
        issue_date = get_date("Enter Issue Date (YYYY-MM-DD): ")
        status = get_certificate_status()

        query = """
            INSERT INTO certificates
            (certificate_id, registration_id, certificate_type,
             issue_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            certificate_id,
            registration_id,
            certificate_type,
            issue_date,
            status
        )

        try:

            cursor.execute(query, values)
            connection.commit()

            print("Certificate added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_certificates():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    certificate_id,
                    registration_id,
                    certificate_type,
                    issue_date,
                    status
                FROM certificates
            """)

            records = cursor.fetchall()

            if records:

                print("\n================ CERTIFICATES ================")

                for record in records:

                    print("----------------------------------------")
                    print("Certificate ID   :", record[0])
                    print("Registration ID  :", record[1])
                    print("Certificate Type :", record[2])
                    print("Issue Date       :", record[3])
                    print("Status           :", record[4])

            else:
                print("No certificate records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_certificate():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        certificate_id = input(
            "Enter Certificate ID to search: "
        )

        try:

            cursor.execute("""
                SELECT
                    certificate_id,
                    registration_id,
                    certificate_type,
                    issue_date,
                    status
                FROM certificates
                WHERE certificate_id = %s
            """, (certificate_id,))

            record = cursor.fetchone()

            if record:

                print("\n========== CERTIFICATE DETAILS ==========")
                print("Certificate ID   :", record[0])
                print("Registration ID  :", record[1])
                print("Certificate Type :", record[2])
                print("Issue Date       :", record[3])
                print("Status           :", record[4])

            else:
                print("Certificate not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_certificate():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        certificate_id = input(
            "Enter Certificate ID to update: "
        )

        try:

            cursor.execute("""
                SELECT certificate_id
                FROM certificates
                WHERE certificate_id = %s
            """, (certificate_id,))

            record = cursor.fetchone()

            if not record:
                print("Certificate not found.")
                cursor.close()
                connection.close()
                return

            registration_id = input("Enter Registration ID: ")
            certificate_type = get_certificate_type()
            issue_date = get_date("Enter Issue Date (YYYY-MM-DD): ")
            status = get_certificate_status()

            query = """
                UPDATE certificates
                SET
                    registration_id = %s,
                    certificate_type = %s,
                    issue_date = %s,
                    status = %s
                WHERE certificate_id = %s
            """

            values = (
                registration_id,
                certificate_type,
                issue_date,
                status,
                certificate_id
            )

            cursor.execute(query, values)
            connection.commit()

            print("Certificate updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_certificate():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        certificate_id = input(
            "Enter Certificate ID to delete: "
        )

        try:

            cursor.execute("""
                DELETE FROM certificates
                WHERE certificate_id = %s
            """, (certificate_id,))

            connection.commit()

            if cursor.rowcount > 0:
                print("Certificate deleted successfully.")
            else:
                print("Certificate not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def certificate_management():

    while True:

        print("\n========================================")
        print("       CERTIFICATE MANAGEMENT")
        print("========================================")
        print("1. Add Certificate")
        print("2. View Certificates")
        print("3. Search Certificate")
        print("4. Update Certificate")
        print("5. Delete Certificate")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_certificate()

        elif choice == "2":
            view_certificates()

        elif choice == "3":
            search_certificate()

        elif choice == "4":
            update_certificate()

        elif choice == "5":
            delete_certificate()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# EXPENSE MANAGEMENT
# ============================================================

def add_expense():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID: ")
        expense_type = input("Enter Expense Type: ")
        amount = get_float("Enter Amount: ")
        expense_date = get_date("Enter Expense Date (YYYY-MM-DD): ")

        query = """
            INSERT INTO expenses
            (event_id, expense_type, amount, expense_date)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            event_id,
            expense_type,
            amount,
            expense_date
        )

        try:

            cursor.execute(query, values)
            connection.commit()

            print("Expense added successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def view_expenses():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        query = """
            SELECT
                event_id,
                expense_type,
                amount,
                expense_date
            FROM expenses
        """

        try:

            cursor.execute(query)
            records = cursor.fetchall()

            if records:

                print("\n================ EXPENSES ================")

                for record in records:

                    print("----------------------------------------")
                    print("Event ID      :", record[0])
                    print("Expense Type  :", record[1])
                    print("Amount        :", record[2])
                    print("Expense Date  :", record[3])

            else:
                print("No expense records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def search_expense():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID to search: ")

        query = """
            SELECT
                event_id,
                expense_type,
                amount,
                expense_date
            FROM expenses
            WHERE event_id = %s
        """

        try:

            cursor.execute(query, (event_id,))
            record = cursor.fetchone()

            if record:

                print("\n========== EXPENSE DETAILS ==========")
                print("Event ID      :", record[0])
                print("Expense Type  :", record[1])
                print("Amount        :", record[2])
                print("Expense Date  :", record[3])

            else:
                print("Expense record not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def update_expense():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID to update expense: ")

        try:

            cursor.execute("""
                SELECT event_id
                FROM expenses
                WHERE event_id = %s
            """, (event_id,))

            record = cursor.fetchone()

            if not record:
                print("Expense record not found.")
                cursor.close()
                connection.close()
                return

            print("\nEnter new expense details:")

            expense_type = input("Enter Expense Type: ")
            amount = get_float("Enter Amount: ")
            expense_date = get_date(
                "Enter Expense Date (YYYY-MM-DD): "
            )

            query = """
                UPDATE expenses
                SET
                    expense_type = %s,
                    amount = %s,
                    expense_date = %s
                WHERE event_id = %s
            """

            values = (
                expense_type,
                amount,
                expense_date,
                event_id
            )

            cursor.execute(query, values)
            connection.commit()

            print("Expense updated successfully.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def delete_expense():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        event_id = input("Enter Event ID to delete expense: ")

        try:

            cursor.execute("""
                DELETE FROM expenses
                WHERE event_id = %s
            """, (event_id,))

            connection.commit()

            if cursor.rowcount > 0:
                print("Expense deleted successfully.")
            else:
                print("Expense record not found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


def expense_management():

    while True:

        print("\n========================================")
        print("          EXPENSE MANAGEMENT")
        print("========================================")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Search Expense")
        print("4. Update Expense")
        print("5. Delete Expense")
        print("6. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_expense()

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            search_expense()

        elif choice == "4":
            update_expense()

        elif choice == "5":
            delete_expense()

        elif choice == "6":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# ANALYTICS - OVERALL SUMMARY
# ============================================================

def overall_summary():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            tables = [
                ("Students", "students"),
                ("Organizers", "organizers"),
                ("Venues", "venues"),
                ("Events", "events"),
                ("Registrations", "registrations"),
                ("Attendance Records", "attendance"),
                ("Feedback Records", "feedback"),
                ("Certificates", "certificates"),
                ("Expenses", "expenses")
            ]

            print("\n========== OVERALL SUMMARY ==========")

            for label, table in tables:

                cursor.execute(
                    f"SELECT COUNT(*) FROM {table}"
                )

                count = cursor.fetchone()[0]

                print(f"{label:<25}: {count}")

            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE status = 'Present'
            """)

            present = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE status = 'Absent'
            """)

            absent = cursor.fetchone()[0]

            total_attendance = present + absent

            if total_attendance > 0:
                attendance_percentage = (
                    present / total_attendance
                ) * 100
            else:
                attendance_percentage = 0

            print("----------------------------------------")
            print("Present                  :", present)
            print("Absent                   :", absent)
            print(
                "Attendance Percentage    : "
                f"{attendance_percentage:.2f}%"
            )

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - EVENT WISE REPORT
# ============================================================

def event_wise_report():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        query = """
            SELECT
                e.event_id,
                e.event_name,
                e.event_date,
                o.name,
                v.venue_name,

                COUNT(DISTINCT r.registration_id),

                COUNT(
                    DISTINCT CASE
                        WHEN a.status = 'Present'
                        THEN a.registration_id
                    END
                ),

                COUNT(
                    DISTINCT CASE
                        WHEN a.status = 'Absent'
                        THEN a.registration_id
                    END
                )

            FROM events e

            LEFT JOIN organizers o
                ON e.organizer_id = o.organizer_id

            LEFT JOIN venues v
                ON e.venue_id = v.venue_id

            LEFT JOIN registrations r
                ON e.event_id = r.event_id

            LEFT JOIN attendance a
                ON r.registration_id = a.registration_id

            GROUP BY
                e.event_id,
                e.event_name,
                e.event_date,
                o.name,
                v.venue_name

            ORDER BY e.event_date
        """

        try:

            cursor.execute(query)
            records = cursor.fetchall()

            if records:

                print("\n========== EVENT-WISE REPORT ==========")

                for record in records:

                    event_id = record[0]
                    event_name = record[1]
                    event_date = record[2]
                    organizer = record[3]
                    venue = record[4]
                    registered = record[5]
                    present = record[6]
                    absent = record[7]

                    if registered > 0:
                        attendance_percentage = (
                            present / registered
                        ) * 100
                    else:
                        attendance_percentage = 0

                    print("----------------------------------------")
                    print("Event ID       :", event_id)
                    print("Event Name     :", event_name)
                    print("Date           :", event_date)
                    print("Organizer      :", organizer)
                    print("Venue          :", venue)
                    print("Registered     :", registered)
                    print("Present        :", present)
                    print("Absent         :", absent)
                    print(
                        "Attendance %   : "
                        f"{attendance_percentage:.2f}%"
                    )

            else:
                print("No event data found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - REGISTRATION ANALYSIS
# ============================================================

def registration_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT COUNT(*)
                FROM registrations
            """)

            total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT
                    e.event_name,
                    COUNT(r.registration_id)
                FROM events e
                LEFT JOIN registrations r
                    ON e.event_id = r.event_id
                GROUP BY e.event_id, e.event_name
                ORDER BY COUNT(r.registration_id) DESC
            """)

            records = cursor.fetchall()

            print("\n========== REGISTRATION ANALYSIS ==========")
            print("Total Registrations :", total)

            print("\nEvent-wise Registrations:")

            for record in records:
                print(
                    f"{record[0]:25} : {record[1]}"
                )

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - ATTENDANCE ANALYSIS
# ============================================================

def attendance_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE status = 'Present'
            """)

            present = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE status = 'Absent'
            """)

            absent = cursor.fetchone()[0]

            total_attendance = present + absent

            if total_attendance > 0:
                percentage = (
                    present / total_attendance
                ) * 100
            else:
                percentage = 0

            print("\n========== ATTENDANCE ANALYSIS ==========")
            print("Present             :", present)
            print("Absent              :", absent)
            print("Total Attendance    :", total_attendance)
            print(
                "Attendance %        : "
                f"{percentage:.2f}%"
            )

            print("\nEvent-wise Attendance:")

            cursor.execute("""
                SELECT
                    e.event_name,

                    COUNT(r.registration_id),

                    COUNT(
                        CASE
                            WHEN a.status = 'Present'
                            THEN 1
                        END
                    ),

                    COUNT(
                        CASE
                            WHEN a.status = 'Absent'
                            THEN 1
                        END
                    )

                FROM events e

                LEFT JOIN registrations r
                    ON e.event_id = r.event_id

                LEFT JOIN attendance a
                    ON r.registration_id = a.registration_id

                GROUP BY
                    e.event_id,
                    e.event_name
            """)

            records = cursor.fetchall()

            for record in records:

                event_name = record[0]
                total = record[1]
                event_present = record[2]
                event_absent = record[3]

                if total > 0:
                    event_percentage = (
                        event_present / total
                    ) * 100
                else:
                    event_percentage = 0

                print("----------------------------------------")
                print("Event       :", event_name)
                print("Registered  :", total)
                print("Present     :", event_present)
                print("Absent      :", event_absent)
                print(
                    "Attendance %:",
                    f"{event_percentage:.2f}%"
                )

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - FEEDBACK ANALYSIS
# ============================================================

def feedback_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT COUNT(*)
                FROM feedback
            """)

            total_feedback = cursor.fetchone()[0]

            cursor.execute("""
                SELECT AVG(rating)
                FROM feedback
            """)

            average_rating = cursor.fetchone()[0]

            if average_rating is None:
                average_rating = 0

            print("\n========== FEEDBACK ANALYSIS ==========")
            print("Total Feedback :", total_feedback)
            print(
                "Average Rating : "
                f"{average_rating:.2f}"
            )

            print("\nRating Distribution:")

            cursor.execute("""
                SELECT
                    rating,
                    COUNT(*)
                FROM feedback
                GROUP BY rating
                ORDER BY rating DESC
            """)

            records = cursor.fetchall()

            for record in records:
                print(
                    f"Rating {record[0]} : {record[1]}"
                )

            print("\nEvent-wise Feedback:")

            cursor.execute("""
                SELECT
                    e.event_name,
                    COUNT(f.registration_id),
                    AVG(f.rating)
                FROM events e

                LEFT JOIN registrations r
                    ON e.event_id = r.event_id

                LEFT JOIN feedback f
                    ON r.registration_id = f.registration_id

                GROUP BY
                    e.event_id,
                    e.event_name
            """)

            records = cursor.fetchall()

            for record in records:

                avg = record[2]

                if avg is None:
                    avg = 0

                print("----------------------------------------")
                print("Event           :", record[0])
                print("Feedback Count  :", record[1])
                print("Average Rating  :", f"{avg:.2f}")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - CERTIFICATE ANALYSIS
# ============================================================

def certificate_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT COUNT(*)
                FROM certificates
            """)

            total = cursor.fetchone()[0]

            print("\n========== CERTIFICATE ANALYSIS ==========")
            print("Total Certificates :", total)

            print("\nCertificate Type:")

            cursor.execute("""
                SELECT
                    certificate_type,
                    COUNT(*)
                FROM certificates
                GROUP BY certificate_type
            """)

            records = cursor.fetchall()

            for record in records:
                print(
                    f"{record[0]:20} : {record[1]}"
                )

            print("\nCertificate Status:")

            cursor.execute("""
                SELECT
                    status,
                    COUNT(*)
                FROM certificates
                GROUP BY status
            """)

            records = cursor.fetchall()

            for record in records:
                print(
                    f"{record[0]:20} : {record[1]}"
                )

            print("\nEvent-wise Certificates:")

            cursor.execute("""
                SELECT
                    e.event_name,
                    COUNT(c.certificate_id)
                FROM events e

                LEFT JOIN registrations r
                    ON e.event_id = r.event_id

                LEFT JOIN certificates c
                    ON r.registration_id = c.registration_id

                GROUP BY
                    e.event_id,
                    e.event_name
            """)

            records = cursor.fetchall()

            for record in records:
                print(
                    f"{record[0]:25} : {record[1]}"
                )

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - EXPENSE ANALYSIS
# ============================================================

def expense_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    COALESCE(SUM(amount), 0)
                FROM expenses
            """)

            total_expense = cursor.fetchone()[0]

            print("\n========== EXPENSE ANALYSIS ==========")
            print(
                "Total Expense :",
                f"₹{total_expense:.2f}"
            )

            print("\nEvent-wise Expenses:")

            cursor.execute("""
                SELECT
                    e.event_name,
                    COALESCE(ex.amount, 0)
                FROM events e
                LEFT JOIN expenses ex
                    ON e.event_id = ex.event_id
            """)

            records = cursor.fetchall()

            for record in records:

                print(
                    f"{record[0]:25} : ₹{record[1]:.2f}"
                )

            print("\nExpense Type Analysis:")

            cursor.execute("""
                SELECT
                    expense_type,
                    SUM(amount)
                FROM expenses
                GROUP BY expense_type
                ORDER BY SUM(amount) DESC
            """)

            records = cursor.fetchall()

            for record in records:

                print(
                    f"{record[0]:25} : ₹{record[1]:.2f}"
                )

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - VENUE ANALYSIS
# ============================================================

def venue_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    v.venue_name,
                    v.location,
                    v.capacity,
                    COUNT(e.event_id)
                FROM venues v

                LEFT JOIN events e
                    ON v.venue_id = e.venue_id

                GROUP BY
                    v.venue_id,
                    v.venue_name,
                    v.location,
                    v.capacity

                ORDER BY COUNT(e.event_id) DESC
            """)

            records = cursor.fetchall()

            print("\n========== VENUE ANALYSIS ==========")

            for record in records:

                print("----------------------------------------")
                print("Venue       :", record[0])
                print("Location    :", record[1])
                print("Capacity    :", record[2])
                print("Events Held :", record[3])

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - ORGANIZER ANALYSIS
# ============================================================

def organizer_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute("""
                SELECT
                    o.name,
                    o.role,
                    COUNT(e.event_id)
                FROM organizers o

                LEFT JOIN events e
                    ON o.organizer_id = e.organizer_id

                GROUP BY
                    o.organizer_id,
                    o.name,
                    o.role

                ORDER BY COUNT(e.event_id) DESC
            """)

            records = cursor.fetchall()

            print("\n========== ORGANIZER ANALYSIS ==========")

            for record in records:

                print("----------------------------------------")
                print("Organizer :", record[0])
                print("Role      :", record[1])
                print("Events    :", record[2])

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS - TOP EVENT ANALYSIS
# ============================================================

def top_event_analysis():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        try:

            # -----------------------------------------------
            # MOST REGISTERED EVENT
            # -----------------------------------------------

            cursor.execute("""
                SELECT
                    e.event_name,
                    COUNT(r.registration_id) AS total
                FROM events e
                LEFT JOIN registrations r
                    ON e.event_id = r.event_id
                GROUP BY e.event_id, e.event_name
                ORDER BY total DESC
                LIMIT 1
            """)

            record = cursor.fetchone()

            print("\n========== TOP EVENT ANALYSIS ==========")

            if record:
                print(
                    "Most Registered Event :",
                    record[0]
                )
                print(
                    "Registrations         :",
                    record[1]
                )

            # -----------------------------------------------
            # HIGHEST ATTENDANCE
            # -----------------------------------------------

            cursor.execute("""
                SELECT
                    e.event_name,
                    COUNT(a.registration_id)
                FROM events e

                LEFT JOIN registrations r
                    ON e.event_id = r.event_id

                LEFT JOIN attendance a
                    ON r.registration_id = a.registration_id

                WHERE a.status = 'Present'

                GROUP BY e.event_id, e.event_name

                ORDER BY COUNT(a.registration_id) DESC

                LIMIT 1
            """)

            record = cursor.fetchone()

            if record:

                print(
                    "\nHighest Attendance Event :",
                    record[0]
                )
                print(
                    "Present Count            :",
                    record[1]
                )

            # -----------------------------------------------
            # HIGHEST RATED EVENT
            # -----------------------------------------------

            cursor.execute("""
                SELECT
                    e.event_name,
                    AVG(f.rating)
                FROM events e

                LEFT JOIN registrations r
                    ON e.event_id = r.event_id

                LEFT JOIN feedback f
                    ON r.registration_id = f.registration_id

                WHERE f.rating IS NOT NULL

                GROUP BY e.event_id, e.event_name

                ORDER BY AVG(f.rating) DESC

                LIMIT 1
            """)

            record = cursor.fetchone()

            if record:

                print(
                    "\nHighest Rated Event :",
                    record[0]
                )
                print(
                    "Average Rating      :",
                    f"{record[1]:.2f}"
                )

            # -----------------------------------------------
            # HIGHEST EXPENSE
            # -----------------------------------------------

            cursor.execute("""
                SELECT
                    e.event_name,
                    ex.amount
                FROM events e

                JOIN expenses ex
                    ON e.event_id = ex.event_id

                ORDER BY ex.amount DESC

                LIMIT 1
            """)

            record = cursor.fetchone()

            if record:

                print(
                    "\nHighest Expense Event :",
                    record[0]
                )
                print(
                    "Expense               :",
                    f"₹{record[1]:.2f}"
                )

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# COMPLETE EVENT REPORT
# ============================================================

def complete_event_report():

    connection = get_database_connection()

    if connection:

        cursor = connection.cursor()

        query = """
            SELECT
                e.event_id,
                e.event_name,
                e.event_date,
                e.description,

                o.name,

                v.venue_name,
                v.capacity,

                COUNT(DISTINCT r.registration_id),

                COUNT(
                    DISTINCT CASE
                        WHEN a.status = 'Present'
                        THEN a.registration_id
                    END
                ),

                COUNT(
                    DISTINCT CASE
                        WHEN a.status = 'Absent'
                        THEN a.registration_id
                    END
                ),

                COUNT(DISTINCT f.registration_id),

                AVG(f.rating),

                COUNT(DISTINCT c.certificate_id),

                COALESCE(ex.amount, 0)

            FROM events e

            LEFT JOIN organizers o
                ON e.organizer_id = o.organizer_id

            LEFT JOIN venues v
                ON e.venue_id = v.venue_id

            LEFT JOIN registrations r
                ON e.event_id = r.event_id

            LEFT JOIN attendance a
                ON r.registration_id = a.registration_id

            LEFT JOIN feedback f
                ON r.registration_id = f.registration_id

            LEFT JOIN certificates c
                ON r.registration_id = c.registration_id

            LEFT JOIN expenses ex
                ON e.event_id = ex.event_id

            GROUP BY
                e.event_id,
                e.event_name,
                e.event_date,
                e.description,
                o.name,
                v.venue_name,
                v.capacity,
                ex.amount

            ORDER BY e.event_date
        """

        try:

            cursor.execute(query)
            records = cursor.fetchall()

            if records:

                print("\n")
                print("======================================================")
                print("              COMPLETE EVENT REPORT")
                print("======================================================")

                for record in records:

                    event_id = record[0]
                    event_name = record[1]
                    event_date = record[2]
                    description = record[3]
                    organizer = record[4]
                    venue = record[5]
                    capacity = record[6]
                    registered = record[7]
                    present = record[8]
                    absent = record[9]
                    feedback_count = record[10]
                    average_rating = record[11]
                    certificates = record[12]
                    expense = record[13]

                    if average_rating is None:
                        average_rating = 0

                    if registered > 0:
                        attendance_percentage = (
                            present / registered
                        ) * 100
                    else:
                        attendance_percentage = 0

                    print("\n------------------------------------------------------")
                    print("Event ID              :", event_id)
                    print("Event Name            :", event_name)
                    print("Event Date            :", event_date)
                    print("Description           :", description)
                    print("Organizer             :", organizer)
                    print("Venue                 :", venue)
                    print("Venue Capacity        :", capacity)
                    print("Registered Students   :", registered)
                    print("Present               :", present)
                    print("Absent                :", absent)

                    print(
                        "Attendance Percentage : "
                        f"{attendance_percentage:.2f}%"
                    )

                    print(
                        "Feedback Count        :",
                        feedback_count
                    )

                    print(
                        "Average Rating        : "
                        f"{average_rating:.2f}"
                    )

                    print(
                        "Certificates Issued   :",
                        certificates
                    )

                    print(
                        "Total Expense         : "
                        f"₹{expense:.2f}"
                    )

                print("------------------------------------------------------")

            else:
                print("No event records found.")

        except mysql.connector.Error as e:
            handle_database_error(e)

        finally:
            cursor.close()
            connection.close()


# ============================================================
# ANALYTICS & REPORTS MENU
# ============================================================

def analytics_reports():

    while True:

        print("\n========================================")
        print("         ANALYTICS & REPORTS")
        print("========================================")
        print("1. Overall Summary")
        print("2. Event-wise Report")
        print("3. Registration Analysis")
        print("4. Attendance Analysis")
        print("5. Feedback Analysis")
        print("6. Certificate Analysis")
        print("7. Expense Analysis")
        print("8. Venue Analysis")
        print("9. Organizer Analysis")
        print("10. Top Event Analysis")
        print("11. Complete Event Report")
        print("12. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            overall_summary()

        elif choice == "2":
            event_wise_report()

        elif choice == "3":
            registration_analysis()

        elif choice == "4":
            attendance_analysis()

        elif choice == "5":
            feedback_analysis()

        elif choice == "6":
            certificate_analysis()

        elif choice == "7":
            expense_analysis()

        elif choice == "8":
            venue_analysis()

        elif choice == "9":
            organizer_analysis()

        elif choice == "10":
            top_event_analysis()

        elif choice == "11":
            complete_event_report()

        elif choice == "12":
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# MAIN MENU
# ============================================================

def main():

    create_database()
    create_tables()

    while True:

        print("\n")
        print("========================================")
        print("   COLLEGE EVENT MANAGEMENT SYSTEM")
        print("========================================")
        print()
        print("1. Student Management")
        print("2. Organizer Management")
        print("3. Venue Management")
        print("4. Event Management")
        print("5. Registration Management")
        print("6. Attendance Management")
        print("7. Feedback Management")
        print("8. Certificate Management")
        print("9. Expense Management")
        print("10. Analytics & Reports")
        print("11. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            student_management()

        elif choice == "2":
            organizer_management()

        elif choice == "3":
            venue_management()

        elif choice == "4":
            event_management()

        elif choice == "5":
            registration_management()

        elif choice == "6":
            attendance_management()

        elif choice == "7":
            feedback_management()

        elif choice == "8":
            certificate_management()

        elif choice == "9":
            expense_management()

        elif choice == "10":
            analytics_reports()

        elif choice == "11":
            print("\nThank you for using College Event Management System!")
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()