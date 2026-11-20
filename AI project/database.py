"""SQLite data access layer for InterviewAce AI."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from config import DATABASE_PATH


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    """Create all tables required by the application."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash BLOB NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                analyzed_skills TEXT DEFAULT '[]',
                analysis_json TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resume_id INTEGER,
                interview_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question_count INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                total_score REAL DEFAULT 0,
                percentage REAL DEFAULT 0,
                final_summary TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                position INTEGER NOT NULL,
                answer TEXT DEFAULT '',
                ai_score REAL,
                feedback TEXT DEFAULT '',
                evaluation_json TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_interviews_user ON interviews(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_questions_interview ON questions(interview_id, position);
            """
        )


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


# Users
def create_user(name: str, email: str, password_hash: bytes) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name.strip(), email.strip().lower(), password_hash, utc_now()),
        )
        return int(cursor.lastrowid)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        return row_to_dict(conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone())


def get_user(user_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        return row_to_dict(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())


# Resumes
def create_resume(
    user_id: int,
    file_path: str,
    file_name: str,
    extracted_text: str,
    analysis: dict[str, Any],
) -> int:
    skills = analysis.get("skills", [])
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO resumes
               (user_id, file_path, file_name, extracted_text, analyzed_skills, analysis_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, file_path, file_name, extracted_text, json.dumps(skills), json.dumps(analysis), utc_now()),
        )
        return int(cursor.lastrowid)


def get_resumes(user_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_resume(resume_id: int, user_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM resumes WHERE id = ? AND user_id = ?", (resume_id, user_id)
        ).fetchone()
    return row_to_dict(row)


# Interviews and questions
def create_interview(
    user_id: int, resume_id: int | None, interview_type: str, difficulty: str, questions: list[str]
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO interviews
               (user_id, resume_id, interview_type, difficulty, question_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, resume_id, interview_type, difficulty, len(questions), utc_now()),
        )
        interview_id = int(cursor.lastrowid)
        conn.executemany(
            """INSERT INTO questions (interview_id, question, position, created_at)
               VALUES (?, ?, ?, ?)""",
            [(interview_id, question, index + 1, utc_now()) for index, question in enumerate(questions)],
        )
    return interview_id


def get_interview(interview_id: int, user_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM interviews WHERE id = ? AND user_id = ?", (interview_id, user_id)
        ).fetchone()
    return row_to_dict(row)


def get_interview_questions(interview_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM questions WHERE interview_id = ? ORDER BY position", (interview_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def save_answer(question_id: int, answer: str, evaluation: dict[str, Any]) -> None:
    score = max(0.0, min(10.0, float(evaluation.get("score", 0))))
    with get_connection() as conn:
        conn.execute(
            """UPDATE questions
               SET answer = ?, ai_score = ?, feedback = ?, evaluation_json = ?
               WHERE id = ?""",
            (answer.strip(), score, str(evaluation.get("feedback", "")), json.dumps(evaluation), question_id),
        )


def complete_interview(interview_id: int, final_summary: str) -> dict[str, float]:
    with get_connection() as conn:
        result = conn.execute(
            "SELECT COALESCE(SUM(ai_score), 0) AS total, COUNT(*) AS count FROM questions WHERE interview_id = ?",
            (interview_id,),
        ).fetchone()
        total = round(float(result["total"]), 2)
        count = int(result["count"])
        percentage = round((total / (count * 10) * 100) if count else 0, 1)
        conn.execute(
            """UPDATE interviews
               SET total_score = ?, percentage = ?, completed_at = ?, final_summary = ?
               WHERE id = ?""",
            (total, percentage, utc_now(), final_summary, interview_id),
        )
    return {"total_score": total, "percentage": percentage, "question_count": count}


def get_user_interviews(user_id: int, limit: int | None = None) -> list[dict[str, Any]]:
    query = "SELECT * FROM interviews WHERE user_id = ? ORDER BY created_at DESC"
    params: list[Any] = [user_id]
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_dashboard_stats(user_id: int) -> dict[str, float | int]:
    with get_connection() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS total_interviews,
                      COALESCE(AVG(percentage), 0) AS average_score,
                      COALESCE(MAX(percentage), 0) AS highest_score,
                      COALESCE(MIN(percentage), 0) AS lowest_score
               FROM interviews
               WHERE user_id = ? AND completed_at IS NOT NULL""",
            (user_id,),
        ).fetchone()
    return {key: round(float(row[key]), 1) if key != "total_interviews" else int(row[key]) for key in row.keys()}


def get_completed_interviews(user_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, interview_type, difficulty, created_at, completed_at, percentage, total_score
               FROM interviews WHERE user_id = ? AND completed_at IS NOT NULL ORDER BY completed_at""",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]
