import sqlite3
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = PROJECT_DIR / "students.db"
TEACHER_PASSWORD = os.getenv("TEACHER_PASSWORD", "786")


class TeacherAccess(BaseModel):
    teacher_name: str
    password: str


def get_connection():
    # read-only mode: the app can never modify the database
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/api/student")
def get_student(
    name: str = Query(...),
    roll: str = Query(...),
    student_class: int = Query(..., alias="class", ge=1, le=12),
):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT name, roll, student_class, total_marks, marks
            FROM students
            WHERE LOWER(name) = LOWER(?) AND roll = ? AND student_class = ?
            """,
            (name.strip(), roll.strip(), student_class),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)


@app.get("/api/top-students")
def get_top_students(student_class: int = Query(..., alias="class", ge=1, le=12)):
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
                WHERE student_class = ? AND marks IS NOT NULL
            )
            WHERE position <= 3
            ORDER BY position, name COLLATE NOCASE, roll
            """,
            (student_class,),
        ).fetchall()
    finally:
        conn.close()

    return [dict(row) for row in rows]


@app.post("/api/teacher/students")
def get_teacher_students(access: TeacherAccess):
    teacher_name = access.teacher_name.strip()
    if not teacher_name:
        raise HTTPException(status_code=422, detail="Teacher name is required")
    if access.password != TEACHER_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect password")

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT name, roll, student_class, total_marks, marks
            FROM students
            ORDER BY student_class, name COLLATE NOCASE, roll
            """
        ).fetchall()
        top_rows = conn.execute(
            """
            SELECT name, roll, student_class, total_marks, marks
            FROM students
            WHERE marks IS NOT NULL
            ORDER BY marks DESC, student_class, name COLLATE NOCASE, roll
            LIMIT 3
            """
        ).fetchall()
    finally:
        conn.close()

    return {
        "teacher_name": teacher_name,
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