"""Gemini integration with dependable local fallbacks for development."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from config import GEMINI_API_KEY, GEMINI_MODEL, PROMPTS_DIR

try:
    from google import genai
    from google.genai import types
except ImportError:  # The rest of the application still works before installation.
    genai = None
    types = None


DEFAULT_ANALYSIS = {
    "skills": [],
    "projects": [],
    "education": [],
    "strengths": [],
    "weaknesses": [],
}


def is_gemini_configured() -> bool:
    return bool(GEMINI_API_KEY and genai)


def _prompt_file(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _json_from_response(text: str) -> dict[str, Any] | list[Any]:
    """Extract JSON even when a provider wraps it in Markdown fences."""
    cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("The AI response was not valid JSON.")
        return json.loads(match.group(1))


def _ask_gemini(prompt: str) -> dict[str, Any] | list[Any]:
    if not is_gemini_configured():
        raise RuntimeError("Gemini is not configured.")
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.35,
            response_mime_type="application/json",
        ),
    )
    return _json_from_response(response.text)


def _normalise_analysis(data: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for field in DEFAULT_ANALYSIS:
        value = data.get(field, [])
        if isinstance(value, str):
            value = [value]
        result[field] = [str(item).strip() for item in value if str(item).strip()]
    return result


def _fallback_analysis(resume_text: str) -> dict[str, list[str]]:
    common_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "SQL", "HTML", "CSS", "React", "Node.js",
        "Django", "Flask", "FastAPI", "Streamlit", "Pandas", "NumPy", "TensorFlow", "PyTorch",
        "Machine Learning", "Data Analysis", "Power BI", "Tableau", "AWS", "Docker", "Git", "Excel",
    ]
    found = [skill for skill in common_skills if re.search(rf"\b{re.escape(skill)}\b", resume_text, re.I)]
    lines = [line.strip(" •-\t") for line in resume_text.splitlines() if line.strip()]
    projects = [line for line in lines if re.search(r"project|built|developed|implemented", line, re.I)][:4]
    education = [line for line in lines if re.search(r"bachelor|master|b\.tech|b\.sc|university|college|gpa", line, re.I)][:3]
    return {
        "skills": found or ["Communication", "Problem Solving"],
        "projects": projects or ["No clearly labeled projects found in the uploaded resume."],
        "education": education or ["Education details were not confidently identified."],
        "strengths": ["Resume includes relevant technical keywords."] if found else ["Resume text was successfully extracted."],
        "weaknesses": ["Add measurable achievements and clearer project outcomes where possible."],
    }


def analyse_resume(resume_text: str) -> dict[str, list[str]]:
    prompt = _prompt_file("resume_prompt.txt").replace("{{resume_text}}", resume_text[:24000])
    try:
        response = _ask_gemini(prompt)
        if not isinstance(response, dict):
            raise ValueError("Expected an analysis object.")
        return _normalise_analysis(response)
    except Exception:
        return _fallback_analysis(resume_text)


QUESTION_BANK: dict[str, list[str]] = {
    "HR": [
        "Tell me about yourself and the experience most relevant to this role.",
        "Describe a time you handled a difficult situation in a team.",
        "What motivates you, and how do you stay productive when priorities change?",
        "Why are you interested in this role and this kind of work?",
        "Tell me about a piece of constructive feedback you received and what you did with it.",
    ],
    "Technical": [
        "Walk me through the design of a project on your resume. What trade-offs did you make?",
        "How do you approach debugging a production issue you cannot reproduce locally?",
        "Explain the difference between a process and a thread, and when it matters.",
        "How would you design a scalable API for a frequently used feature?",
        "Describe a time you improved the reliability or performance of a system.",
    ],
    "Python": [
        "What is the difference between a list, tuple, and set in Python?",
        "Explain generators and give an example of when you would use one.",
        "How do Python decorators work, and what problem do they solve?",
        "What are common pitfalls of mutable default arguments?",
        "How would you profile and speed up a slow Python data-processing task?",
    ],
    "AI/ML": [
        "Explain the bias-variance trade-off and how you would diagnose overfitting.",
        "How would you choose evaluation metrics for an imbalanced classification problem?",
        "Describe an end-to-end machine-learning project you have built or would build.",
        "What is data leakage, and how would you prevent it?",
        "How would you monitor an ML model after deployment?",
    ],
    "Data Science": [
        "How do you clean and validate a dataset before analysis?",
        "Explain the difference between correlation and causation with an example.",
        "How would you communicate an uncertain data finding to a non-technical stakeholder?",
        "What is the purpose of a train, validation, and test split?",
        "Describe how you would investigate a sudden drop in a business metric.",
    ],
}


def _fallback_questions(
    skills: list[str], interview_type: str, difficulty: str, question_count: int
) -> list[str]:
    pool = QUESTION_BANK.get(interview_type, QUESTION_BANK["Technical"])
    if interview_type == "Custom":
        pool = QUESTION_BANK["Technical"] + QUESTION_BANK["HR"]
    skill_clause = f" Relate your answer to {skills[0]}." if skills else ""
    difficulty_clause = {
        "Easy": " Keep the explanation clear and foundational.",
        "Medium": " Include a concrete example and relevant trade-offs.",
        "Hard": " Include edge cases, trade-offs, and how you would validate your approach.",
    }.get(difficulty, "")
    questions: list[str] = []
    for index in range(question_count):
        base = pool[index % len(pool)]
        questions.append(base + (skill_clause if index % 2 == 0 else difficulty_clause))
    return questions


def generate_questions(
    resume_text: str,
    skills: list[str],
    interview_type: str,
    difficulty: str,
    question_count: int,
    custom_focus: str = "",
) -> list[str]:
    prompt = _prompt_file("question_prompt.txt")
    prompt = (prompt.replace("{{resume_text}}", resume_text[:18000])
                    .replace("{{skills}}", ", ".join(skills))
                    .replace("{{interview_type}}", interview_type)
                    .replace("{{difficulty}}", difficulty)
                    .replace("{{question_count}}", str(question_count))
                    .replace("{{custom_focus}}", custom_focus or "None"))
    try:
        response = _ask_gemini(prompt)
        if isinstance(response, dict):
            response = response.get("questions", [])
        questions = [str(item).strip() for item in response if str(item).strip()] if isinstance(response, list) else []
        if len(questions) >= question_count:
            return questions[:question_count]
        raise ValueError("AI returned too few questions.")
    except Exception:
        return _fallback_questions(skills, interview_type, difficulty, question_count)


def _score_from_value(value: Any) -> float:
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    return max(0.0, min(10.0, float(match.group()))) if match else 0.0


def _as_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _fallback_evaluation(question: str, answer: str) -> dict[str, Any]:
    words = re.findall(r"\b[\w+#.-]+\b", answer.lower())
    unique_words = set(words)
    question_words = set(re.findall(r"\b[\w+#.-]+\b", question.lower()))
    overlap = len(unique_words & question_words)
    length_score = min(len(words) / 45, 1) * 4
    structure_bonus = min(sum(token in answer.lower() for token in ("example", "because", "result", "first", "then")), 3) * 0.7
    score = round(min(9.0, 2.5 + length_score + structure_bonus + min(overlap, 3) * 0.4), 1)
    if len(words) < 12:
        score = min(score, 4.0)
    feedback = "Your answer addresses the prompt." if len(words) >= 25 else "Your answer is very brief; expand it with an explanation and example."
    return {
        "score": score,
        "feedback": feedback + " This development-mode evaluation is a heuristic; configure Gemini for tailored feedback.",
        "strengths": ["Stayed focused on the question."] if overlap else ["Submitted an answer for review."],
        "missing_points": ["Use a concrete example, the action you took, and the result."],
        "correct_answer": "A strong answer explains the concept clearly, supports it with an example, and notes relevant trade-offs.",
        "suggestions": ["Use the STAR structure: situation, task, action, result.", "State assumptions and quantify impact where possible."],
        "confidence": "Moderate" if len(words) >= 40 else "Developing",
    }


def evaluate_answer(question: str, answer: str, interview_type: str, difficulty: str) -> dict[str, Any]:
    prompt = (_prompt_file("evaluation_prompt.txt")
              .replace("{{question}}", question)
              .replace("{{answer}}", answer[:12000])
              .replace("{{interview_type}}", interview_type)
              .replace("{{difficulty}}", difficulty))
    try:
        response = _ask_gemini(prompt)
        if not isinstance(response, dict):
            raise ValueError("Expected an evaluation object.")
        return {
            "score": _score_from_value(response.get("score", 0)),
            "feedback": str(response.get("feedback", "")),
            "strengths": _as_list(response.get("strengths", [])),
            "missing_points": _as_list(response.get("missing_points", [])),
            "correct_answer": str(response.get("correct_answer", "")),
            "suggestions": _as_list(response.get("suggestions", [])),
            "confidence": str(response.get("confidence", "")),
        }
    except Exception:
        return _fallback_evaluation(question, answer)


def make_final_summary(evaluations: list[dict[str, Any]], percentage: float) -> str:
    if not evaluations:
        return "No answers were submitted. Start another interview when you are ready."
    all_strengths = [item for evaluation in evaluations for item in evaluation.get("strengths", [])]
    all_missing = [item for evaluation in evaluations for item in evaluation.get("missing_points", [])]
    strength = Counter(map(str, all_strengths)).most_common(1)
    improvement = Counter(map(str, all_missing)).most_common(1)
    level = "strong" if percentage >= 75 else "developing" if percentage >= 50 else "early-stage"
    summary = f"This was a {level} interview performance at {percentage:.1f}%."
    if strength:
        summary += f" A recurring strength was: {strength[0][0]}"
    if improvement:
        summary += f" Focus next on: {improvement[0][0]}"
    return summary
