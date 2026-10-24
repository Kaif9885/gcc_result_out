import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "students.db"

CREATE_STUDENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT NOT NULL,
        total_marks INTEGER NOT NULL,
        marks INTEGER,
        student_class INTEGER NOT NULL DEFAULT 1
            CHECK (student_class BETWEEN 1 AND 12)
    )
"""

OLD_SAMPLE_KEYS = {
    ("Rahul Sharma", "101"),
    ("Priya Singh", "102"),
    ("Amit Kumar", "103"),
}

CLASS_10_ROSTER = [
    ("Bittu Kumar", 22),
    ("Ankit Kumar", 28),
    ("Anjit Kumar", None),
    ("Ranjeet Kumar", None),
    ("Suraj Kumar", None),
    ("Rohit Kumar", None),
    ("Vishnujeet Kumar", 19),
    ("Prince Kumar", None),
    ("Nitesh Kumar", 30),
    ("Md Umar", None),
    ("Jamir Ali", None),
    ("Golu Kumar", None),
    ("Md Altamash", None),
    ("Sameer Khan", 29),
    ("Saif Raza", None),
    ("Anshul Kumar", None),
    ("Sumant Kumar", 18),
    ("Parwez Ali", 20),
    ("Umar Azad", 35),
    ("Raiyan Ali", 15),
    ("Sahil Ali", 30),
    ("Himanshu Kushw", 38),
    ("Anshu Kumar", 47),
    ("Md Nehal", 18),
]


with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute(CREATE_STUDENTS_TABLE.format(table_name="students"))
    columns = {row[1]: row for row in cur.execute("PRAGMA table_info(students)")}

    if "student_class" not in columns:
        cur.execute("""
            ALTER TABLE students
            ADD COLUMN student_class INTEGER NOT NULL DEFAULT 1
                CHECK (student_class BETWEEN 1 AND 12)
        """)

    if columns["marks"][3]:
        cur.execute("ALTER TABLE students RENAME TO students_legacy")
        cur.execute(CREATE_STUDENTS_TABLE.format(table_name="students"))
        cur.execute("""
            INSERT INTO students (id, name, roll, total_marks, marks, student_class)
            SELECT id, name, roll, total_marks, marks, student_class
            FROM students_legacy
        """)
        cur.execute("DROP TABLE students_legacy")

    existing_keys = set(cur.execute("SELECT name, roll FROM students").fetchall())
    if not existing_keys or existing_keys == OLD_SAMPLE_KEYS:
        cur.execute("DELETE FROM students")
        cur.executemany(
            """
            INSERT INTO students (name, roll, total_marks, marks, student_class)
            VALUES (?, ?, 60, ?, 10)
            """,
            [
                (name, str(roll), marks)
                for roll, (name, marks) in enumerate(CLASS_10_ROSTER, start=1)
            ],
        )

print("students.db ready with the Class 10 roster")