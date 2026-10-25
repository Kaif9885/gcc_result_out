import sqlite3
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_DIRECTORY = Path(os.getenv("RENDER_DISK_PATH", PROJECT_DIR))
DB_DIRECTORY.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIRECTORY / "students.db"

CREATE_STUDENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT NOT NULL,
        total_marks INTEGER NOT NULL,
        marks INTEGER,
        student_class INTEGER NOT NULL DEFAULT 1
            CHECK (student_class BETWEEN 1 AND 12),
        board TEXT,
        subject TEXT,
        chapter TEXT,
        class_section TEXT NOT NULL DEFAULT ''
    )
"""

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

    columns = {row[1]: row for row in cur.execute("PRAGMA table_info(students)")}
    for column_name, column_type in (
        ("board", "TEXT"),
        ("subject", "TEXT"),
        ("chapter", "TEXT"),
        ("class_section", "TEXT NOT NULL DEFAULT ''"),
    ):
        if column_name not in columns:
            cur.execute(f"ALTER TABLE students ADD COLUMN {column_name} {column_type}")

print("students.db schema ready")