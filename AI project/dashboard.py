"""Dashboard and analytics components."""
from __future__ import annotations

from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_completed_interviews, get_dashboard_stats, get_user_interviews
from utils import navigate, page_heading


def render_dashboard(user: dict) -> None:
    """Render the candidate's command centre and practice history."""
    stats = get_dashboard_stats(user["id"])
    first_name = escape(user["name"].split()[0])
    st.markdown(
        f"<section class='dashboard-hero'><div class='hero-copy'><div class='eyebrow'>Your interview workspace</div>"
        f"<h1>Good to see you, {first_name}.</h1>"
        "<p>Small, deliberate sessions build the calm and clarity that interviews reward.</p></div>"
        "<div class='hero-signal'><span class='signal-orb'>*</span><div><small>YOUR NEXT BEST STEP</small>"
        "<strong>Start a focused practice session</strong><span>Pick a role, difficulty and depth.</span></div></div>"
        "</section>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='eyebrow section-label'>Continue building</div><h2>Choose your next move</h2>",
        unsafe_allow_html=True,
    )
    setup, resume, reports, analytics = st.columns(4, gap="medium")
    with setup:
        with st.container(border=True):
            st.markdown("<div class='action-icon'>01</div><h3>New practice</h3>", unsafe_allow_html=True)
            st.write("Create a tailored interview from your resume.")
            if st.button("Start practice", type="primary", use_container_width=True):
                navigate("Interview Setup")
    with resume:
        with st.container(border=True):
            st.markdown("<div class='action-icon'>02</div><h3>Resume studio</h3>", unsafe_allow_html=True)
            st.write("Refresh the profile that guides every question.")
            if st.button("Manage resume", use_container_width=True):
                navigate("My Resume")
    with reports:
        with st.container(border=True):
            st.markdown("<div class='action-icon'>03</div><h3>Review reports</h3>", unsafe_allow_html=True)
            st.write("Revisit feedback and turn it into better answers.")
            if st.button("Open reports", use_container_width=True):
                navigate("Final Report")
    with analytics:
        with st.container(border=True):
            st.markdown("<div class='action-icon'>04</div><h3>See progress</h3>", unsafe_allow_html=True)
            st.write("Watch your confidence build across sessions.")
            if st.button("View analytics", use_container_width=True):
                navigate("Analytics")

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='eyebrow'>Performance snapshot</div><h2>Progress at a glance</h2>", unsafe_allow_html=True)
    metrics = st.columns(4, gap="medium")
    metrics[0].metric("Completed interviews", stats["total_interviews"])
    metrics[1].metric("Average score", f"{stats['average_score']:.1f}%")
    metrics[2].metric("Best score", f"{stats['highest_score']:.1f}%")
    metrics[3].metric("Lowest score", f"{stats['lowest_score']:.1f}%")

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='eyebrow'>Your practice history</div><h2>Recent interviews</h2>", unsafe_allow_html=True)
    recent = get_user_interviews(user["id"], limit=5)
    if not recent:
        st.markdown(
            "<div class='empty-state'><div class='empty-icon'>GO</div>"
            "<h3>Your first practice session is waiting</h3>"
            "<p>Upload your resume, choose an interview type, and get a report that shows exactly where to improve.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    frame = pd.DataFrame(recent)
    frame["Status"] = frame["completed_at"].apply(
        lambda value: "Completed" if value else "In progress"
    )
    frame["Score"] = frame.apply(
        lambda row: f"{row['percentage']:.1f}%" if row["completed_at"] else "-",
        axis=1,
    )
    frame["Date"] = pd.to_datetime(frame["created_at"]).dt.strftime("%d %b %Y")
    st.dataframe(
        frame[["Date", "interview_type", "difficulty", "question_count", "Score", "Status"]].rename(
            columns={
                "interview_type": "Type",
                "difficulty": "Difficulty",
                "question_count": "Questions",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


def render_analytics(user: dict) -> None:
    page_heading(
        "Performance intelligence",
        "See your progress take shape",
        "Use your interview history to spot patterns, reinforce strengths, and decide what to practise next.",
    )
    interviews = get_completed_interviews(user["id"])
    if not interviews:
        st.markdown(
            "<div class='empty-state'><div class='empty-icon'>0%</div>"
            "<h3>Analytics unlock after your first interview</h3>"
            "<p>Complete a practice session to see your scores over time and by interview type.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    frame = pd.DataFrame(interviews)
    frame["date"] = pd.to_datetime(frame["completed_at"])
    frame["label"] = frame.apply(
        lambda row: f"{row['interview_type']} / {row['difficulty']}",
        axis=1,
    )
    overview = st.columns(3, gap="medium")
    overview[0].metric("Sessions", len(frame))
    overview[1].metric("Latest score", f"{frame.iloc[-1]['percentage']:.1f}%")
    overview[2].metric("Score change", f"{frame.iloc[-1]['percentage'] - frame.iloc[0]['percentage']:+.1f}%")

    chart = px.line(
        frame,
        x="date",
        y="percentage",
        markers=True,
        hover_name="label",
        hover_data={"total_score": ":.1f", "percentage": ":.1f", "date": False},
        labels={"date": "Interview date", "percentage": "Score (%)"},
        color_discrete_sequence=["#6957e8"],
    )
    chart.update_yaxes(range=[0, 100], gridcolor="#e9ebf3")
    chart.update_xaxes(gridcolor="#ffffff")
    chart.update_layout(
        title="Score progression",
        plot_bgcolor="rgba(255,255,255,.72)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=55, b=10),
        height=390,
    )
    st.plotly_chart(chart, use_container_width=True)

    by_type = frame.groupby("interview_type", as_index=False)["percentage"].mean()
    bar = px.bar(
        by_type,
        x="interview_type",
        y="percentage",
        text_auto=".1f",
        labels={"interview_type": "Interview type", "percentage": "Average score (%)"},
        color_discrete_sequence=["#00adbb"],
    )
    bar.update_yaxes(range=[0, 100], gridcolor="#e9ebf3")
    bar.update_layout(
        title="Average score by interview type",
        plot_bgcolor="rgba(255,255,255,.72)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        height=340,
    )
    st.plotly_chart(bar, use_container_width=True)
