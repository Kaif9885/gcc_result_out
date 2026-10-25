import sqlite3
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")
app = FastAPI()
DB_DIRECTORY = Path(os.getenv("RENDER_DISK_PATH", PROJECT_DIR))
DB_PATH = DB_DIRECTORY / "students.db"
DATABASE_URL = os.getenv("DATABASE_URL")
TEACHER_PASSWORD = os.getenv("TEACHER_PASSWORD", "786")


@app.get("/health")
def health_check():
    return {"status": "ok"}


class TeacherAccess(BaseModel):
    teacher_name: str
    password: str
    student_class: int
    class_section: str = ""
    board: str
    subject: str
    chapter: str


def get_connection():
    if DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(DATABASE_URL, row_factory=dict_row)

    # read-only mode: the app can never modify the database
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/api/student")
def get_student(
    name: str = Query(...),
    roll: str = Query(...),
    student_class: int = Query(..., alias="class", ge=1, le=12),
    board: str = Query(...),
    subject: str = Query(...),
    chapter: str = Query(...),
    class_section: str = Query("", alias="section"),
):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT name, roll, student_class, total_marks, marks,
                board, subject, chapter, class_section
            FROM students
            WHERE LOWER(name) = LOWER(?) AND roll = ? AND student_class = ?
                AND board = ? AND subject = ? AND chapter = ?
                AND COALESCE(class_section, '') = ?
            """,
            (
                name.strip(), roll.strip(), student_class,
                board.strip(), subject.strip(), chapter.strip(), class_section.strip().lower(),
            ),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)


@app.get("/api/top-students")
def get_top_students(
    student_class: int = Query(..., alias="class", ge=1, le=12),
    board: str = Query(...),
    subject: str = Query(...),
    chapter: str = Query(...),
    class_section: str = Query("", alias="section"),
):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT name, roll, total_marks, marks, position
            FROM (
                SELECT
                    name,
                    roll,
                    total_marks,
                    marks,
                    student_class,
                    DENSE_RANK() OVER (ORDER BY marks DESC) AS position
                FROM students
                WHERE student_class = ? AND COALESCE(class_section, '') = ?
                    AND board = ? AND subject = ? AND chapter = ?
                    AND marks IS NOT NULL
            )
            WHERE position <= 3
            ORDER BY position, name COLLATE NOCASE, roll
            """,
            (student_class, class_section.strip().lower(), board.strip(), subject.strip(), chapter.strip()),
        ).fetchall()
    finally:
        conn.close()

    return [dict(row) for row in rows]


@app.post("/api/teacher/students")
def get_teacher_students(access: TeacherAccess):
    teacher_name = access.teacher_name.strip()
    class_section = access.class_section.strip().lower()
    if not teacher_name:
        raise HTTPException(status_code=422, detail="Teacher name is required")
    if not 1 <= access.student_class <= 12:
        raise HTTPException(status_code=422, detail="Select a valid class")
    if access.board not in {"BSEB", "CBSE"}:
        raise HTTPException(status_code=422, detail="Select a valid board")
    if access.subject not in {"Biology", "Chemistry", "Physics"}:
        raise HTTPException(status_code=422, detail="Select a valid subject")
    if not access.chapter.strip():
        raise HTTPException(status_code=422, detail="Select a chapter")
    if access.student_class == 10 and class_section not in {"boys", "girls"}:
        raise HTTPException(status_code=422, detail="Select Class 10 Boys or Girls")
    if access.student_class != 10:
        class_section = ""
    if access.password != TEACHER_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect password")

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT name, roll, student_class, total_marks, marks
            FROM students
            WHERE student_class = ? AND COALESCE(class_section, '') = ?
                AND board = ? AND subject = ? AND chapter = ?
            ORDER BY CAST(roll AS INTEGER), roll COLLATE NOCASE
            """,
            (access.student_class, class_section, access.board, access.subject, access.chapter),
        ).fetchall()
        top_rows = conn.execute(
            """
            SELECT name, roll, student_class, total_marks, marks, position
            FROM (
                SELECT
                    name,
                    roll,
                    student_class,
                    total_marks,
                    marks,
                    DENSE_RANK() OVER (ORDER BY marks DESC) AS position
                FROM students
                WHERE student_class = ? AND COALESCE(class_section, '') = ?
                    AND board = ? AND subject = ? AND chapter = ?
                    AND marks IS NOT NULL
            )
            WHERE position <= 3
            ORDER BY position, name COLLATE NOCASE, roll
            """,
            (access.student_class, class_section, access.board, access.subject, access.chapter),
        ).fetchall()
    finally:
        conn.close()

    return {
        "teacher_name": teacher_name,
        "student_class": access.student_class,
        "class_section": class_section,
        "board": access.board,
        "subject": access.subject,
        "chapter": access.chapter,
        "students": [dict(row) for row in rows],
        "top_students": [dict(row) for row in top_rows],
    }


@app.get("/")
def home():
    return FileResponse(PROJECT_DIR / "static" / "index.html")


@app.get("/result")
def result_page():
    return FileResponse(PROJECT_DIR / "static" / "result.html")


@app.get("/teacher")
def teacher_page():
    return FileResponse(PROJECT_DIR / "static" / "teacher.html")


app.mount("/static", StaticFiles(directory=PROJECT_DIR / "static"), name="static")