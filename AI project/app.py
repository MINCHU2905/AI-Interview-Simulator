"""InterviewAce AI Streamlit application entry point."""
from __future__ import annotations

from html import escape

import streamlit as st

from ai_service import analyse_resume, is_gemini_configured
from auth import authenticate_user, register_user, validate_registration
from dashboard import render_analytics, render_dashboard
from database import create_resume, get_resumes, init_db
from interview import render_session, render_setup
from report import render_report
from resume_parser import extract_pdf_text, save_uploaded_resume
from utils import inject_theme, navigate, page_heading, parse_json


st.set_page_config(page_title="InterviewAce AI", page_icon="🎯", layout="wide")


def render_auth() -> None:
    """Render the public welcome, registration, and sign-in experience."""
    st.markdown(
        "<div class='auth-topline'><div class='auth-wordmark'><span class='auth-mark'>IA</span>"
        "<span>InterviewAce</span></div><div class='auth-topline-note'><span class='live-dot'></span>"
        "Your private practice workspace</div></div>",
        unsafe_allow_html=True,
    )
    intro, panel = st.columns([1.05, 0.95], gap="large")

    with intro:
        st.markdown(
            "<div class='auth-showcase'>"
            "<div class='auth-kicker'><span class='live-dot'></span>AI interview practice, built around you</div>"
            "<h1>Make every interview<br><em>your strongest one.</em></h1>"
            "<p>Turn your resume into focused practice, useful feedback, and a clear plan "
            "for showing up with confidence.</p>"
            "<div class='auth-points'><span>Resume-aware questions</span>"
            "<span>Instant coaching</span><span>Progress analytics</span></div>"
            "<div class='auth-proof'><div><strong>01</strong><span>Upload your resume</span></div>"
            "<div><strong>02</strong><span>Practise with purpose</span></div>"
            "<div><strong>03</strong><span>Track your growth</span></div></div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with panel:
        with st.container(border=True):
            st.markdown(
                "<div class='eyebrow'>Your practice starts here</div>"
                "<h2>Build interview confidence.</h2>"
                "<p>Sign in to continue, or create a workspace in a minute.</p>",
                unsafe_allow_html=True,
            )
            login_tab, register_tab = st.tabs(["Log in", "Create account"])

            with login_tab:
                with st.form("login_form"):
                    email = st.text_input(
                        "Email",
                        key="login_email",
                        placeholder="you@example.com",
                    )
                    password = st.text_input(
                        "Password",
                        type="password",
                        key="login_password",
                        placeholder="Enter your password",
                    )
                    submitted = st.form_submit_button(
                        "Log in to your workspace",
                        type="primary",
                        use_container_width=True,
                    )
                if submitted:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.nav_page = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Incorrect email or password.")

            with register_tab:
                with st.form("register_form", clear_on_submit=True):
                    name = st.text_input("Full name", placeholder="Your name")
                    email = st.text_input("Email address", placeholder="you@example.com")
                    password = st.text_input(
                        "Password",
                        type="password",
                        help="Use at least 8 characters.",
                        placeholder="At least 8 characters",
                    )
                    confirmation = st.text_input("Confirm password", type="password")
                    submitted = st.form_submit_button(
                        "Create my free workspace",
                        type="primary",
                        use_container_width=True,
                    )
                if submitted:
                    error = validate_registration(name, email, password, confirmation)
                    if error:
                        st.error(error)
                    else:
                        register_user(name, email, password)
                        st.success("Account created. You can now log in.")
            st.markdown(
                "<div class='auth-panel-footer'><span class='shield-icon'>✓</span>"
                "Your practice history stays in your personal workspace.</div>",
                unsafe_allow_html=True,
            )


def render_resume_page(user: dict) -> None:
    page_heading(
        "Candidate profile",
        "Your resume, made actionable",
        "Upload a text-based PDF once, then use its insights to generate more relevant interview practice.",
    )
    st.markdown(
        "<div class='feature-band'><div><span class='feature-number'>01</span><strong>Upload</strong>"
        "<small>A text-based PDF resume</small></div><div><span class='feature-number'>02</span>"
        "<strong>Analyse</strong><small>Skills, projects and growth areas</small></div>"
        "<div><span class='feature-number'>03</span><strong>Practise</strong>"
        "<small>Questions tailored to your profile</small></div></div>",
        unsafe_allow_html=True,
    )

    if not is_gemini_configured():
        st.info(
            "Gemini is not configured, so this session will use the built-in development fallback. "
            "Add GEMINI_API_KEY to .env for AI-generated analysis and feedback."
        )

    with st.container(border=True):
        st.subheader("Upload a new resume")
        st.caption("PDF only · text-based files · up to 10 MB")
        uploaded_file = st.file_uploader(
            "Choose a resume PDF",
            type=["pdf"],
            help="Maximum file size: 10 MB",
        )
        if uploaded_file and st.button("Analyse resume", type="primary"):
            try:
                with st.spinner("Extracting text and analysing your resume..."):
                    path = save_uploaded_resume(uploaded_file, user["id"])
                    text = extract_pdf_text(path)
                    analysis = analyse_resume(text)
                    resume_id = create_resume(
                        user["id"],
                        str(path),
                        uploaded_file.name,
                        text,
                        analysis,
                    )
                st.session_state.active_resume_id = resume_id
                st.success("Resume saved and analysed successfully.")
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                st.error(f"We could not process this resume: {error}")

    resumes = get_resumes(user["id"])
    if not resumes:
        st.markdown(
            "<div class='empty-state'><div class='empty-icon'>01</div>"
            "<h3>Your practice profile starts here</h3>"
            "<p>Upload a resume and we will identify the skills and experience to use in your interviews.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    st.subheader("Your saved profile")
    resume_ids = [item["id"] for item in resumes]
    active_id = st.session_state.get("active_resume_id")
    default = resume_ids.index(active_id) if active_id in resume_ids else 0
    selected_id = st.selectbox(
        "Select a resume to review",
        resume_ids,
        index=default,
        format_func=lambda value: next(
            item["file_name"] for item in resumes if item["id"] == value
        ),
    )
    selected = next(item for item in resumes if item["id"] == selected_id)
    st.session_state.active_resume_id = selected_id
    analysis = parse_json(selected["analysis_json"], {})

    fields = [
        ("Skills", "skills", "01"),
        ("Projects", "projects", "02"),
        ("Education", "education", "03"),
        ("Strengths", "strengths", "04"),
        ("Growth opportunities", "weaknesses", "05"),
    ]
    columns = st.columns(3, gap="medium")
    for index, (label, field, number) in enumerate(fields):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"<div class='eyebrow'>{number}</div><h3>{label}</h3>", unsafe_allow_html=True)
                values = analysis.get(field, [])
                if values:
                    for value in values:
                        st.write(f"• {value}")
                else:
                    st.caption("No information identified.")

    with st.expander("View extracted resume text"):
        st.text(selected["extracted_text"])
    if st.button("Use this resume for an interview", type="primary"):
        navigate("Interview Setup")


def render_sidebar(user: dict) -> str:
    with st.sidebar:
        st.markdown(
            "<div class='side-brand'><div class='brand-mark'>IA</div><div>"
            "<div class='brand-name'>InterviewAce</div>"
            "<div class='brand-subtitle'>Career practice studio</div></div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='side-user'>{escape(user['name'])}<span>Personal workspace</span></div>",
            unsafe_allow_html=True,
        )
        pages = [
            "Dashboard",
            "My Resume",
            "Interview Setup",
            "Interview Session",
            "Final Report",
            "Analytics",
        ]
        if "nav_page" not in st.session_state:
            st.session_state.nav_page = "Dashboard"
        selected = st.radio(
            "Main navigation",
            pages,
            key="nav_page",
            label_visibility="collapsed",
        )
        st.divider()
        status = "Gemini connected" if is_gemini_configured() else "Development fallback active"
        st.markdown(
            f"<div class='side-status'><span class='live-dot'></span>{status}</div>",
            unsafe_allow_html=True,
        )
        if st.button("Log out", use_container_width=True):
            for key in (
                "user",
                "active_interview_id",
                "active_resume_id",
                "report_interview_id",
                "requested_page",
                "nav_page",
            ):
                st.session_state.pop(key, None)
            st.rerun()
    return selected


def main() -> None:
    init_db()
    inject_theme()
    user = st.session_state.get("user")
    if not user:
        render_auth()
        return
    if "requested_page" in st.session_state:
        st.session_state.nav_page = st.session_state.pop("requested_page")
    page = render_sidebar(user)
    if page == "Dashboard":
        render_dashboard(user)
    elif page == "My Resume":
        render_resume_page(user)
    elif page == "Interview Setup":
        render_setup(user)
    elif page == "Interview Session":
        render_session(user)
    elif page == "Final Report":
        render_report(user, st.session_state.get("report_interview_id"))
    elif page == "Analytics":
        render_analytics(user)


if __name__ == "__main__":
    main()
