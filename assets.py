import sqlite3 as sq
from datetime import datetime
import json

class Database:

    def __init__(self, connection=None):
        if connection:
            self.connection = connection
        else:
            self.connection = sq.connect("student.db")

    def attendance(self, rollno, sub):
        cursor = self.connection.cursor()
        if sub == "all":
            update_query = """
                UPDATE ATTENDANCE
                SET
                    cs1 = cs1 + 1,
                    cs2 = cs2 + 1,
                    cs3 = cs3 + 1,
                    cs4 = cs4 + 1,
                    cs5 = cs5 + 1
                WHERE rollno = ?;
                """
        else:
            update_query = f"""UPDATE ATTENDANCE SET {sub} = {sub} +1 WHERE rollno = ?;"""
        cursor.execute(update_query, (rollno,))
        self.connection.commit()

    def mark_only_present(self, roll: list, sub):
        """
        Mark attendance as present for specified roll numbers in the given subject
        and update the attendance history, ensuring the subject is recorded as present.
        """
        cursor = self.connection.cursor()
        date = datetime.now().strftime("%Y-%m-%d")

        for rollno in roll:
            cursor.execute(f"UPDATE ATTENDANCE SET {sub} = {sub} + 1 WHERE rollno = ?", (rollno,))

            cursor.execute("SELECT history FROM ATTENDANCE WHERE rollno = ?", (rollno,))
            result = cursor.fetchone()

            # Check if a result is returned, otherwise initialize history
            history = result[0] if result else '{}'

            history = json.loads(history) if history != '{}' else {date: []}

            if date not in history:
                history[date] = []

            if sub not in history[date]:
                history[date].append(sub)

            cursor.execute(
                "UPDATE ATTENDANCE SET history = ? WHERE rollno = ?",
                (json.dumps(history), rollno)
            )

        self.connection.commit()

    def mark_only_absent(self, roll: list, sub):
        """
        Mark attendance as absent for all roll numbers except the ones in the list,
        and update the attendance history to reflect the absence for the specified subject.
        """
        cursor = self.connection.cursor()
        date = datetime.now().strftime("%Y-%m-%d")

        placeholders = ', '.join(['?'] * len(roll))
        cursor.execute(f"""
            UPDATE ATTENDANCE
            SET {sub} = {sub} + 1
            WHERE rollno NOT IN ({placeholders})
        """, roll)

        cursor.execute("SELECT rollno, history FROM ATTENDANCE")
        rows = cursor.fetchall()

        for rollno, history in rows:
            if rollno in roll:
                continue

            history = json.loads(history) if history != '{}' else {date: []}

            if date not in history:
                history[date] = []

            if sub not in history[date]:
                history[date].append(sub)

            cursor.execute(
                "UPDATE ATTENDANCE SET history = ? WHERE rollno = ?",
                (json.dumps(history), rollno)
            )

        self.connection.commit()

    def rollinit(self, rollno, name, email):
        data = (rollno, name, email, 0, 0, 0, 0, 0,"{}")
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO ATTENDANCE values (?,?,?,?,?,?,?,?,?)", data)
        self.connection.commit()

    def reset_attendance(self,roll, sub):
        x = '{}'
        data = (roll,)
        cursor = self.connection.cursor()
        cursor.execute("UPDATE ATTENDANCE set %s=0, history='{}' where rollno =?"%sub,data)
        self.connection.commit()


class Fetch(Database):
    def fetch_subject_attendance(self, roll, sub):
        cur = self.connection.cursor()
        cur.execute(f"SELECT {sub} FROM ATTENDANCE where rollno = ?", (roll,))
        x = cur.fetchone()[0]
        return x

    def fetch_all_attendance(self, roll):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM ATTENDANCE where rollno = ?", (roll,))
        x = cur.fetchone()
        x = [i for i in x]
        return x

    def fetch_all_rolls(self):
        cur = self.connection.cursor()
        cur.execute(f"SELECT rollno FROM ATTENDANCE")
        x = cur.fetchall()
        x = [i[0] for i in x]
        return x

    def fetch_daily_absentees(self, date, sub):
        """
        Fetch the list of roll numbers of students who were absent on a specific date
        for a specific subject.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT rollno, history FROM ATTENDANCE")
        rows = cursor.fetchall()

        absent_rollnos = []

        for rollno, history in rows:
            try:
                if history == '{}':
                    absent_rollnos.append(rollno[-3:])
                    continue

                history_dict = json.loads(history)

                if date not in history_dict:
                    absent_rollnos.append(rollno[-3:])
                    continue
                if date in history_dict and sub not in history_dict[date]:
                    absent_rollnos.append(rollno[-3:])

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error processing roll number {rollno}: {e}")

        return absent_rollnos

    def fetch_daily_absentees_with_mail(self, date, sub):
        """
        Fetch the list of roll numbers of students who were absent on a specific date
        for a specific subject.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT rollno,email,history FROM ATTENDANCE")
        rows = cursor.fetchall()

        absent_rollnos = {}

        for rollno, email, history in rows:
            try:
                if history == '{}':
                    absent_rollnos[rollno] = email
                    continue

                history_dict = json.loads(history)

                if date not in history_dict:
                    absent_rollnos[rollno] = email
                    continue
                if date in history_dict and sub not in history_dict[date]:
                    absent_rollnos[rollno] = email

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error processing roll number {rollno}: {e}")

        return absent_rollnos
