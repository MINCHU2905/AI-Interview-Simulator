"""Interview setup and one-question-at-a-time interview session UI."""
from __future__ import annotations

from html import escape

import streamlit as st

from ai_service import evaluate_answer, generate_questions, make_final_summary
from database import (
    complete_interview,
    create_interview,
    get_interview,
    get_interview_questions,
    get_resume,
    get_resumes,
    save_answer,
)
from utils import navigate, page_heading, parse_json


def render_setup(user: dict) -> None:
    page_heading(
        "Practice builder",
        "Set up your next interview",
        "Choose the role, difficulty, and depth of practice. Your selected resume will keep the questions personal.",
    )
    resumes = get_resumes(user["id"])
    if not resumes:
        st.markdown(
            "<div class='empty-state'><div class='empty-icon'>01</div>"
            "<h3>Start with your resume</h3>"
            "<p>Upload and analyse a resume first so we can tailor the practice to your skills and experience.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Upload my resume", type="primary"):
            navigate("My Resume")
        return

    resume_ids = [item["id"] for item in resumes]
    active_id = st.session_state.get("active_resume_id")
    resume_index = resume_ids.index(active_id) if active_id in resume_ids else 0
    st.markdown(
        "<div class='setup-guide'><span class='setup-guide-mark'>*</span><div><strong>Make it yours</strong>"
        "<span>Choose a role, set the challenge level, and decide how deep you want to go.</span>"
        "</div></div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        with st.form("interview_setup"):
            st.markdown("<div class='eyebrow'>Interview settings</div>", unsafe_allow_html=True)
            resume_id = st.selectbox(
                "Resume",
                resume_ids,
                index=resume_index,
                format_func=lambda value: next(
                    item["file_name"] for item in resumes if item["id"] == value
                ),
            )
            first, second, third = st.columns(3, gap="medium")
            with first:
                interview_type = st.selectbox(
                    "Interview type",
                    ["HR", "Technical", "Python", "AI/ML", "Data Science", "Custom"],
                )
                st.caption("Choose the conversation you want to practise.")
            with second:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
                st.caption("Set the level that will stretch you most.")
            with third:
                question_count = st.selectbox("Questions", [5, 10, 15], index=0)
                st.caption("Short warm-up or a full practice session.")
            custom_focus = st.text_input(
                "Custom focus (optional)",
                placeholder="e.g., backend APIs, SQL, product analytics",
            )
            submitted = st.form_submit_button(
                "Generate my interview",
                type="primary",
                use_container_width=True,
            )

    if not submitted:
        return
    resume = get_resume(resume_id, user["id"])
    if not resume:
        st.error("The selected resume could not be found.")
        return
    analysis = parse_json(resume["analysis_json"], {})
    with st.spinner("Creating personalized questions..."):
        questions = generate_questions(
            resume["extracted_text"],
            analysis.get("skills", []),
            interview_type,
            difficulty,
            int(question_count),
            custom_focus,
        )
        interview_id = create_interview(
            user["id"], resume_id, interview_type, difficulty, questions
        )
    st.session_state.active_interview_id = interview_id
    st.session_state.active_resume_id = resume_id
    navigate("Interview Session")


def _render_evaluation(evaluation: dict) -> None:
    st.success(f"Answer evaluated — {float(evaluation.get('score', 0)):.1f}/10")
    feedback = escape(str(evaluation.get("feedback", "")))
    st.markdown(f"<div class='feedback-box'>{feedback}</div>", unsafe_allow_html=True)
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            st.markdown("<div class='eyebrow'>What worked</div>", unsafe_allow_html=True)
            for item in evaluation.get("strengths", []):
                st.write(f"• {item}")
    with right:
        with st.container(border=True):
            st.markdown("<div class='eyebrow'>Improve next time</div>", unsafe_allow_html=True)
            for item in evaluation.get("missing_points", []):
                st.write(f"• {item}")


def render_session(user: dict) -> None:
    interview_id = st.session_state.get("active_interview_id")
    if not interview_id:
        page_heading(
            "Practice session",
            "Nothing in progress yet",
            "Set up a tailored interview whenever you are ready to practise.",
        )
        if st.button("Set up an interview", type="primary"):
            navigate("Interview Setup")
        return
    interview = get_interview(interview_id, user["id"])
    if not interview:
        st.session_state.pop("active_interview_id", None)
        st.error("This interview is unavailable.")
        return
    questions = get_interview_questions(interview_id)
    unanswered = next((item for item in questions if item["ai_score"] is None), None)
    review = st.session_state.get("answer_review")
    if review and review.get("interview_id") == interview_id:
        page_heading(
            "Instant feedback",
            "A closer look at your answer",
            f"Question {review['position']} of {len(questions)} has been evaluated.",
        )
        _render_evaluation(review["evaluation"])
        is_last = review["position"] == len(questions)
        if st.button(
            "Finish interview" if is_last else "Continue to next question",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.pop("answer_review", None)
            st.rerun()
        return

    if unanswered is None:
        evaluations = [parse_json(item["evaluation_json"], {}) for item in questions]
        if not interview["completed_at"]:
            result = complete_interview(
                interview_id,
                make_final_summary(
                    evaluations,
                    sum(float(item["ai_score"] or 0) for item in questions)
                    / (len(questions) * 10)
                    * 100,
                ),
            )
            interview["total_score"] = result["total_score"]
            interview["percentage"] = result["percentage"]
        if st.session_state.get("celebrated_interview") != interview_id:
            st.balloons()
            st.session_state.celebrated_interview = interview_id
        page_heading(
            "Interview complete",
            "Your results are ready",
            "You have finished every question. Explore the details to turn this practice into measurable progress.",
        )
        score, percentage, questions_count = st.columns(3, gap="medium")
        score.metric("Total score", f"{interview['total_score']:.1f}/{len(questions) * 10}")
        percentage.metric("Percentage", f"{interview['percentage']:.1f}%")
        questions_count.metric("Questions answered", len(questions))
        if st.button("View full report", type="primary"):
            st.session_state.report_interview_id = interview_id
            st.session_state.pop("active_interview_id", None)
            navigate("Final Report")
        return

    completed_count = sum(item["ai_score"] is not None for item in questions)
    st.markdown(
        "<div class='eyebrow'>Live practice session</div>"
        f"<h1>Question {unanswered['position']}</h1>"
        f"<p>{escape(interview['interview_type'])} · {escape(interview['difficulty'])} difficulty</p>",
        unsafe_allow_html=True,
    )
    st.progress(
        completed_count / len(questions),
        text=f"{completed_count} of {len(questions)} answered",
    )
    with st.container(border=True):
        st.markdown(
            "<div class='question-card-label'><span>YOUR PROMPT</span><span>Take your time</span></div>",
            unsafe_allow_html=True,
        )
        st.subheader(unanswered["question"])
        answer_key = f"answer_{unanswered['id']}"
        answer = st.text_area(
            "Your answer",
            key=answer_key,
            height=220,
            placeholder="Take a moment, then write your answer here...",
        )
        if st.button("Submit answer for evaluation", type="primary", use_container_width=True):
            if len(answer.strip()) < 4:
                st.warning("Please enter a more complete answer before submitting.")
                return
            with st.spinner("Reviewing your answer..."):
                evaluation = evaluate_answer(
                    unanswered["question"],
                    answer,
                    interview["interview_type"],
                    interview["difficulty"],
                )
                save_answer(unanswered["id"], answer, evaluation)
            st.session_state.answer_review = {
                "interview_id": interview_id,
                "position": unanswered["position"],
                "evaluation": evaluation,
            }
            st.rerun()
