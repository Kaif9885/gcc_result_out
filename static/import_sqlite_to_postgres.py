"""Copy local students.db records into PostgreSQL configured by DATABASE_URL."""

import os
import sqlite3
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")
SQLITE_PATH = Path(os.getenv("SQLITE_DB_PATH", PROJECT_DIR / "students.db"))
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise SystemExit("Set DATABASE_URL to your Supabase PostgreSQL connection string first.")
if not SQLITE_PATH.exists():
    raise SystemExit(f"Local database file not found: {SQLITE_PATH}")

with sqlite3.connect(SQLITE_PATH) as source:
    source.row_factory = sqlite3.Row
    rows = source.execute(
        """
        SELECT name, roll, total_marks, marks, student_class,
            COALESCE(board, '') AS board,
            COALESCE(subject, '') AS subject,
            COALESCE(chapter, '') AS chapter,
            COALESCE(class_section, '') AS class_section
        FROM students
        """
    ).fetchall()

if not rows:
    raise SystemExit("Local database has no student records to import.")

with psycopg.connect(DATABASE_URL) as destination:
    destination.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            total_marks INTEGER NOT NULL,
            marks INTEGER,
            student_class INTEGER NOT NULL DEFAULT 1
                CHECK (student_class BETWEEN 1 AND 12),
            board TEXT NOT NULL,
            subject TEXT NOT NULL,
            chapter TEXT NOT NULL,
            class_section TEXT NOT NULL DEFAULT ''
        )
        """
    )
    destination.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS students_result_identity
        ON students (student_class, class_section, board, subject, chapter, roll)
        """
    )

    # The app requires board/subject/chapter; do not silently import incomplete rows.
    incomplete = [row["roll"] for row in rows if not all(row[key] for key in ("board", "subject", "chapter"))]
    if incomplete:
        raise SystemExit(
            "Some local records are missing board, subject, or chapter; "
            f"fill those fields before importing. Incomplete roll numbers: {', '.join(incomplete[:20])}"
        )

    with destination.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO students (
                name, roll, total_marks, marks, student_class,
                board, subject, chapter, class_section
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_class, class_section, board, subject, chapter, roll)
            DO UPDATE SET
                name = EXCLUDED.name,
                total_marks = EXCLUDED.total_marks,
                marks = EXCLUDED.marks
            """,
            [tuple(row) for row in rows],
        )

print(f"Imported/updated {len(rows)} student result records in Supabase PostgreSQL.")
