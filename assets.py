import sqlite3 as sq


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

    def mark_only_absent(self, roll: list, sub):
        """
        Increment the attendance for a given subject for all roll numbers
        except those in the provided list.
        """
        cursor = self.connection.cursor()

        placeholders = ', '.join(['?'] * len(roll))
        update_query = f"""
               UPDATE ATTENDANCE
               SET {sub} = {sub} + 1
               WHERE rollno NOT IN ({placeholders});
           """

        cursor.execute(update_query, roll)
        self.connection.commit()

    def mark_only_present(self, roll: list, sub):
        """
        Increment the attendance for a given subject only for roll numbers
        in the provided list.
        """
        cursor = self.connection.cursor()

        placeholders = ', '.join(['?'] * len(roll))
        update_query = f"""
               UPDATE ATTENDANCE
               SET {sub} = {sub} + 1
               WHERE rollno IN ({placeholders});
           """

        cursor.execute(update_query, roll)
        self.connection.commit()

    def rollinit(self, rollno, name, email):
        data = (rollno, name, email, 0, 0, 0, 0, 0)
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO ATTENDANCE values (?,?,?,?,?,?,?,?)", data)
        self.connection.commit()
    def reset_attendance(self,roll, sub):
        data = (roll,)
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE ATTENDANCE set {sub}=0 where rollno =?", data)
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



