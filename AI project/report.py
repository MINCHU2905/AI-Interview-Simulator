"""Final interview-report presentation."""
from __future__ import annotations

from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_interview, get_interview_questions, get_user_interviews
from utils import page_heading, parse_json, score_label


def _bullet_items(items: list[str], fallback: str) -> None:
    if not items:
        st.write(fallback)
        return
    for item in items:
        st.write(f"• {item}")


def render_report(user: dict, preferred_interview_id: int | None = None) -> None:
    completed = [item for item in get_user_interviews(user["id"]) if item["completed_at"]]
    if not completed:
        page_heading(
            "Interview reports",
            "No reports just yet",
            "Complete a practice session to receive a detailed, question-by-question review.",
        )
        return

    page_heading(
        "Interview reports",
        "A detailed view of your performance",
        "Review each answer, identify recurring patterns, and carry the most useful lessons into your next session.",
    )
    ids = [item["id"] for item in completed]
    default_index = ids.index(preferred_interview_id) if preferred_interview_id in ids else 0
    selection = st.selectbox(
        "Choose an interview report",
        options=ids,
        index=default_index,
        format_func=lambda interview_id: next(
            f"{item['interview_type']} · {item['difficulty']} · {item['created_at'][:10]}"
            for item in completed
            if item["id"] == interview_id
        ),
    )
    interview = get_interview(selection, user["id"])
    if not interview:
        st.error("That report is no longer available.")
        return
    questions = get_interview_questions(selection)
    evaluations = [parse_json(question["evaluation_json"], {}) for question in questions]

    st.caption(
        f"{interview['interview_type']} · {interview['difficulty']} · completed {interview['completed_at']}"
    )
    st.markdown(
        "<div class='score-ribbon'><div><span>INTERVIEW OUTCOME</span>"
        f"<strong>{score_label(float(interview['percentage']))}</strong></div>"
        f"<div class='score-ribbon-number'>{interview['percentage']:.0f}<small>%</small></div>"
        "<p>Use this review to turn one focused practice session into a more confident next answer.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    one, two, three = st.columns(3, gap="medium")
    one.metric("Overall score", f"{interview['total_score']:.1f}/{interview['question_count'] * 10}")
    two.metric("Percentage", f"{interview['percentage']:.1f}%")
    three.metric("Assessment", score_label(float(interview["percentage"])))

    scores = pd.DataFrame(
        {
            "Question": [f"Q{item['position']}" for item in questions],
            "Score": [item["ai_score"] or 0 for item in questions],
        }
    )
    graph = px.bar(
        scores,
        x="Question",
        y="Score",
        text_auto=".1f",
        range_y=[0, 10],
        color_discrete_sequence=["#5b5ce2"],
    )
    graph.update_yaxes(gridcolor="#edf0f7")
    graph.update_layout(
        title="Question-by-question score",
        plot_bgcolor="rgba(255,255,255,.72)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        height=320,
    )
    st.plotly_chart(graph, use_container_width=True)

    st.markdown("<div class='eyebrow'>Interview summary</div><h2>What your performance shows</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='feedback-box'>{escape(interview['final_summary'])}</div>",
        unsafe_allow_html=True,
    )
    strengths = [str(value) for evaluation in evaluations for value in evaluation.get("strengths", [])]
    missing = [str(value) for evaluation in evaluations for value in evaluation.get("missing_points", [])]
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            st.markdown("<div class='eyebrow'>Keep building</div><h3>Strengths</h3>", unsafe_allow_html=True)
            _bullet_items(
                list(dict.fromkeys(strengths))[:5],
                "Review the detailed answers below for specific wins.",
            )
    with right:
        with st.container(border=True):
            st.markdown("<div class='eyebrow'>Practise next</div><h3>Recommended focus</h3>", unsafe_allow_html=True)
            _bullet_items(
                list(dict.fromkeys(missing))[:5],
                "Continue practising answers with concrete examples.",
            )

    st.markdown("<div class='eyebrow'>Question review</div><h2>Detailed feedback</h2>", unsafe_allow_html=True)
    for question, evaluation in zip(questions, evaluations):
        with st.expander(
            f"Q{question['position']} · {question['ai_score']:.1f}/10 — {question['question']}"
        ):
            st.markdown("**Your answer**")
            st.write(question["answer"])
            st.markdown("**Feedback**")
            st.write(evaluation.get("feedback", question["feedback"]))
            st.markdown("**Missing points**")
            _bullet_items(evaluation.get("missing_points", []), "No specific missing points recorded.")
            st.markdown("**Suggested answer**")
            st.write(evaluation.get("correct_answer", "Not available."))
            st.markdown("**Improvement tips**")
            _bullet_items(evaluation.get("suggestions", []), "Keep answers structured and concise.")
