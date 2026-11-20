"""Small presentation and data helpers shared across UI modules."""
from __future__ import annotations

import json
from html import escape
from typing import Any

import streamlit as st


def parse_json(value: str | None, default: Any) -> Any:
    try:
        return json.loads(value or "")
    except (TypeError, json.JSONDecodeError):
        return default


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ace-ink: #17203a;
            --ace-muted: #69738a;
            --ace-primary: #5b5ce2;
            --ace-primary-dark: #4144ba;
            --ace-cyan: #12b6c9;
            --ace-surface: #ffffff;
            --ace-line: #e7e9f3;
            --ace-wash: #f6f7fe;
        }

        .stApp {
            background:
                radial-gradient(circle at 87% 4%, rgba(92, 93, 226, .13), transparent 21rem),
                radial-gradient(circle at 8% 42%, rgba(18, 182, 201, .08), transparent 22rem),
                #f8f9fd;
            color: var(--ace-ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 2.4rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: var(--ace-ink) !important;
            letter-spacing: -.035em;
        }

        h1 { font-weight: 760 !important; }
        h2, h3 { font-weight: 700 !important; }

        p, [data-testid="stCaptionContainer"] {
            color: var(--ace-muted);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #101936 0%, #172554 56%, #1b2050 100%);
            border-right: 0;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 1.45rem .85rem 1rem;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #c8d1ee !important;
        }

        .side-brand {
            display: flex;
            align-items: center;
            gap: .72rem;
            margin: .1rem .35rem 1.7rem;
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 2.4rem;
            height: 2.4rem;
            border-radius: .78rem;
            background: linear-gradient(135deg, #8b8cff 0%, #39d8e6 100%);
            color: #111936;
            font-weight: 800;
            letter-spacing: -.08em;
            box-shadow: 0 10px 24px rgba(37, 221, 235, .18);
        }

        .brand-name { color: #ffffff; font-size: 1.05rem; font-weight: 750; line-height: 1.1; }
        .brand-subtitle { color: #9eacd4; font-size: .71rem; letter-spacing: .06em; text-transform: uppercase; }

        .side-user {
            padding: .85rem;
            margin: 0 .25rem 1.25rem;
            border: 1px solid rgba(188, 203, 255, .16);
            border-radius: .9rem;
            background: rgba(255, 255, 255, .07);
            color: #ffffff;
            font-size: .88rem;
        }

        .side-user span { color: #aebbe0; display: block; font-size: .71rem; margin-top: .18rem; }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: .2rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: .7rem;
            padding: .18rem .15rem;
            transition: background .2s ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255,255,255,.09);
        }

        [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
            border-color: #9ba5ff !important;
        }

        [data-testid="stSidebar"] [data-baseweb="radio"] input:checked + div {
            background-color: #817dff !important;
        }

        [data-testid="stMetric"] {
            padding: 1.15rem 1.2rem;
            background: rgba(255, 255, 255, .88);
            border: 1px solid var(--ace-line);
            border-radius: 1rem;
            box-shadow: 0 9px 26px rgba(26, 35, 71, .045);
        }

        [data-testid="stMetricLabel"] {
            color: var(--ace-muted);
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: var(--ace-primary);
            font-weight: 760;
        }

        .ace-hero {
            padding: .5rem 0 1.4rem;
        }

        .ace-hero h1 {
            margin: 0 0 .45rem;
        }

        .eyebrow {
            color: var(--ace-primary);
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .11em;
            text-transform: uppercase;
        }

        .dashboard-hero {
            position: relative;
            overflow: hidden;
            padding: 2.2rem 2.3rem;
            border-radius: 1.45rem;
            color: #fff;
            background: linear-gradient(120deg, #171f49 0%, #33358d 62%, #635be0 100%);
            box-shadow: 0 22px 44px rgba(48, 49, 137, .18);
            margin-bottom: 1.3rem;
        }

        .dashboard-hero:after {
            content: '';
            position: absolute;
            width: 21rem;
            height: 21rem;
            right: -7rem;
            top: -12rem;
            border: 1px solid rgba(255,255,255,.17);
            border-radius: 50%;
            box-shadow: 0 0 0 2.8rem rgba(255,255,255,.035), 0 0 0 5.6rem rgba(255,255,255,.025);
        }

        .dashboard-hero h1, .dashboard-hero p, .dashboard-hero .eyebrow { color: #fff !important; }
        .dashboard-hero h1 { font-size: clamp(2rem, 4vw, 3rem); max-width: 40rem; margin: .4rem 0 .55rem; }
        .dashboard-hero p { color: rgba(255,255,255,.75) !important; max-width: 32rem; margin-bottom: 0; }
        .dashboard-hero .eyebrow { color: #a8f0f4 !important; }

        .page-heading { margin: .25rem 0 1.65rem; }
        .page-heading h1 { margin: .35rem 0 .35rem; }
        .page-heading p { max-width: 43rem; margin: 0; }

        .action-card, .content-card, .auth-card, .empty-state {
            background: rgba(255, 255, 255, .9);
            border: 1px solid var(--ace-line);
            border-radius: 1.1rem;
            box-shadow: 0 12px 32px rgba(25, 35, 75, .045);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 1.1rem !important;
            border-color: var(--ace-line) !important;
            background: rgba(255, 255, 255, .88);
            box-shadow: 0 12px 32px rgba(25, 35, 75, .045);
        }

        .action-card {
            min-height: 8.7rem;
            padding: 1.25rem;
        }

        .action-card .action-icon {
            display: grid;
            place-items: center;
            width: 2.25rem;
            height: 2.25rem;
            margin-bottom: .85rem;
            border-radius: .72rem;
            background: #eeefff;
            color: var(--ace-primary);
            font-weight: 800;
        }

        .action-card h3 { font-size: 1rem; margin: 0 0 .25rem; letter-spacing: -.02em; }
        .action-card p { font-size: .83rem; line-height: 1.5; margin: 0; }

        .empty-state { text-align: center; padding: 2.6rem 1.5rem; }
        .empty-state .empty-icon { color: var(--ace-primary); font-size: 2rem; font-weight: 800; }
        .empty-state h3 { margin: .55rem 0 .35rem; }
        .empty-state p { margin: 0 auto; max-width: 30rem; }

        .auth-page { min-height: 77vh; display: flex; align-items: center; }
        .auth-showcase { padding: 3rem .9rem 3rem 1rem; }
        .auth-showcase h1 { font-size: clamp(2.65rem, 5vw, 4.65rem); line-height: .98; margin: .75rem 0 1rem; max-width: 41rem; }
        .auth-showcase p { font-size: 1.05rem; line-height: 1.65; max-width: 31rem; }
        .auth-points { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.45rem; }
        .auth-points span { border: 1px solid #e0e4f2; background: rgba(255,255,255,.78); border-radius: 99px; padding: .42rem .72rem; color: #4f5870; font-size: .79rem; font-weight: 650; }
        .auth-card { padding: 1.65rem; }
        .auth-card h2 { margin: .2rem 0 .25rem; }

        .stButton > button {
            min-height: 2.7rem;
            border-radius: .72rem;
            border: 1px solid #dfe3f1;
            font-weight: 700;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(38, 47, 116, .12);
            border-color: #bfc5e8;
        }

        .stButton > button[kind="primary"] {
            color: #fff;
            border: 0;
            background: linear-gradient(110deg, var(--ace-primary-dark), #6d69f0 58%, #5f87f2);
            box-shadow: 0 9px 20px rgba(82, 80, 210, .22);
        }

        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-baseweb="textarea"] {
            border-radius: .72rem !important;
            border-color: #dfe3f0 !important;
            background: rgba(255,255,255,.9) !important;
        }

        [data-baseweb="input"] > div:focus-within,
        [data-baseweb="textarea"]:focus-within {
            border-color: #8f8bef !important;
            box-shadow: 0 0 0 3px rgba(91,92,226,.11) !important;
        }

        [data-testid="stFileUploader"] {
            border: 1px dashed #bfc5e8;
            border-radius: 1rem;
            padding: .45rem;
            background: rgba(255,255,255,.62);
        }

        [data-baseweb="tab-list"] { gap: .35rem; }
        [data-baseweb="tab"] { border-radius: .55rem; font-weight: 700; padding: .45rem .7rem; }
        [data-baseweb="tab-highlight"] { background: var(--ace-primary) !important; height: 2px !important; }

        [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
            border: 1px solid var(--ace-line);
            border-radius: 1rem;
            overflow: hidden;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--ace-line);
            border-radius: .9rem;
            background: rgba(255,255,255,.76);
        }

        .score-card {
            border: 1px solid #e4e7fa;
            border-radius: 1rem;
            padding: 1rem 1.15rem;
            background: #f9f9ff;
        }

        .feedback-box {
            border-left: 4px solid var(--ace-primary);
            background: #f2f2ff;
            color: #404867;
            padding: 1rem 1.1rem;
            border-radius: 0 .8rem .8rem 0;
            line-height: 1.55;
        }

        /* Professional visual system */
        :root {
            --ace-ink: #17213e;
            --ace-muted: #6b7591;
            --ace-primary: #6957e8;
            --ace-primary-dark: #5140c7;
            --ace-cyan: #00adbb;
            --ace-line: #e4e7f0;
            --ace-wash: #f3f4fb;
        }

        .stApp {
            background:
                radial-gradient(circle at 92% -2%, rgba(105, 87, 232, .18), transparent 25rem),
                radial-gradient(circle at -7% 31%, rgba(0, 173, 187, .10), transparent 23rem),
                linear-gradient(180deg, #fbfcff 0%, #f5f6fc 58%, #f9f9fe 100%);
        }
        .block-container { width: 100%; max-width: 1200px; padding: 2.15rem 1.5rem 4rem; }
        h1, h2, h3 { letter-spacing: -.045em; }
        h1 { line-height: 1.02; }
        h2 { font-size: clamp(1.45rem, 2vw, 2rem); }
        .eyebrow { color: #6957e8; font-size: .68rem; letter-spacing: .14em; }
        .section-label { margin-top: 1.4rem; }
        .section-spacer { height: 1.55rem; }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 110% 4%, rgba(118, 103, 255, .35), transparent 16rem),
                linear-gradient(180deg, #0c1532 0%, #101b42 52%, #142755 100%);
        }
        [data-testid="stSidebar"] > div:first-child { padding: 1.45rem .9rem 1.15rem; }
        .brand-mark {
            width: 2.7rem; height: 2.7rem; border-radius: .92rem;
            background: linear-gradient(145deg, #b1a6ff, #55d8e3);
            box-shadow: 0 12px 28px rgba(84, 103, 255, .28);
        }
        .brand-name { font-size: 1.13rem; letter-spacing: -.04em; }
        .brand-subtitle { font-size: .62rem; letter-spacing: .11em; }
        .side-user { padding: .95rem; border-radius: 1rem; background: rgba(255,255,255,.075); }
        .side-status { display: flex; align-items: center; gap: .45rem; color: #bac6ec; font-size: .72rem; font-weight: 700; }
        .live-dot { display: inline-block; width: .46rem; height: .46rem; border-radius: 99px; background: #5ae0c2; box-shadow: 0 0 0 4px rgba(90,224,194,.12); }
        [data-testid="stSidebar"] [role="radiogroup"] label { padding: .36rem .32rem; border-radius: .75rem; }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,.11); }

        [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] {
            border-color: rgba(225, 228, 239, .98) !important;
            background: rgba(255, 255, 255, .82) !important;
            box-shadow: 0 18px 42px rgba(28, 38, 77, .055) !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] { transition: transform .2s ease, box-shadow .2s ease; }
        [data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: 0 21px 50px rgba(28, 38, 77, .08) !important; }
        [data-testid="stForm"] { border-radius: 1.25rem; padding: .35rem .15rem .2rem; }
        [data-testid="stMetric"] { border-radius: 1.15rem; box-shadow: 0 14px 34px rgba(28, 38, 77, .055); }
        [data-testid="stMetricValue"] { letter-spacing: -.045em; }
        [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label, [data-testid="stTextArea"] label {
            font-size: .76rem; font-weight: 750; color: #45506f;
        }
        [data-baseweb="input"] > div, [data-baseweb="select"] > div, [data-baseweb="textarea"] {
            min-height: 2.85rem; border-radius: .85rem !important; background: #fcfcff !important;
        }
        [data-baseweb="textarea"] { min-height: auto; }
        .stButton > button { min-height: 2.82rem; border-radius: .82rem; }
        .stButton > button[kind="primary"] {
            background: linear-gradient(115deg, #4e3cc5 0%, #705eea 55%, #627ef1 100%);
            box-shadow: 0 12px 24px rgba(85, 68, 207, .25);
        }
        .stButton > button[kind="primary"]:hover { box-shadow: 0 15px 28px rgba(85, 68, 207, .34); }

        .auth-topline { display: flex; align-items: center; justify-content: space-between; margin: .05rem 0 1.5rem; }
        .auth-wordmark { display: flex; align-items: center; gap: .65rem; color: #17213e; font-size: 1rem; font-weight: 800; letter-spacing: -.035em; }
        .auth-mark { display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: .65rem; color: #111a3a; background: linear-gradient(145deg, #ab9fff, #55dbe3); font-size: .7rem; letter-spacing: -.08em; }
        .auth-topline-note, .auth-kicker { display: flex; align-items: center; gap: .55rem; color: #697491; font-size: .76rem; font-weight: 650; }
        .auth-showcase { padding: 3.2rem 1.5rem 2.4rem .45rem; }
        .auth-showcase h1 { max-width: 40rem; font-size: clamp(2.85rem, 4.65vw, 4.9rem); line-height: .95; margin: 1rem 0 1.1rem; }
        .auth-showcase h1 em { font-style: normal; color: #6957e8; }
        .auth-showcase p { max-width: 32rem; font-size: 1.04rem; line-height: 1.7; }
        .auth-points { margin-top: 1.65rem; }
        .auth-points span { padding: .48rem .78rem; border: 1px solid #e2e5f1; background: rgba(255,255,255,.78); box-shadow: 0 7px 20px rgba(42,49,91,.04); }
        .auth-proof { display: flex; gap: .75rem; margin-top: 2.45rem; max-width: 37rem; }
        .auth-proof > div { flex: 1; min-height: 5.75rem; padding: .85rem .9rem; border: 1px solid #e6e8f2; border-radius: 1rem; background: rgba(255,255,255,.58); }
        .auth-proof strong { display: block; color: #6957e8; font-size: 1.1rem; letter-spacing: -.04em; }
        .auth-proof span { display: block; margin-top: .25rem; color: #53607c; font-size: .72rem; font-weight: 650; line-height: 1.4; }
        .auth-panel-footer { display: flex; align-items: center; gap: .5rem; margin: 1.25rem .1rem .1rem; color: #65708b; font-size: .72rem; line-height: 1.45; }
        .shield-icon { display: grid; place-items: center; flex: 0 0 auto; width: 1.35rem; height: 1.35rem; border-radius: 99px; background: #e7f9f4; color: #20856f; font-weight: 900; }

        .feature-band { display: grid; grid-template-columns: repeat(3, 1fr); gap: .55rem; margin: -.35rem 0 1.35rem; padding: .75rem; border: 1px solid #e6e8f1; border-radius: 1.1rem; background: rgba(255,255,255,.68); }
        .feature-band > div { padding: .15rem .55rem; border-right: 1px solid #e8eaf2; }
        .feature-band > div:last-child { border: 0; }
        .feature-band strong, .feature-band small { display: block; }
        .feature-band strong { margin-top: .1rem; font-size: .82rem; color: #2b3658; }
        .feature-band small { color: #78829b; font-size: .68rem; line-height: 1.4; }
        .feature-number { color: #6957e8; font-size: .65rem; font-weight: 850; letter-spacing: .1em; }

        .dashboard-hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(17rem, .8fr); gap: 2rem; align-items: center; padding: 2.65rem 2.8rem; border-radius: 1.65rem; background: linear-gradient(120deg, #111c43 0%, #293674 55%, #6957e8 125%); }
        .dashboard-hero:after { right: -6rem; top: -10rem; width: 23rem; height: 23rem; }
        .dashboard-hero h1 { font-size: clamp(2.25rem, 4.1vw, 3.45rem); }
        .hero-signal { position: relative; z-index: 1; display: flex; gap: .85rem; align-items: center; padding: 1rem; border: 1px solid rgba(255,255,255,.17); border-radius: 1.15rem; background: rgba(255,255,255,.08); backdrop-filter: blur(10px); }
        .signal-orb { display: grid; place-items: center; flex: 0 0 auto; width: 2.7rem; height: 2.7rem; border-radius: .85rem; color: #101c46; background: linear-gradient(145deg, #b1a7ff, #6de1e6); font-size: 1.15rem; }
        .hero-signal small, .hero-signal strong, .hero-signal span { display: block; }
        .hero-signal small { color: #c8d1ff; font-size: .6rem; font-weight: 800; letter-spacing: .1em; }
        .hero-signal strong { margin: .25rem 0; color: #fff; font-size: .87rem; line-height: 1.25; }
        .hero-signal span { color: #d4daf4; font-size: .7rem; }
        [data-testid="stVerticalBlockBorderWrapper"] h3 { font-size: 1rem; margin: .2rem 0 .38rem; }
        [data-testid="stVerticalBlockBorderWrapper"] p { font-size: .78rem; line-height: 1.55; }
        .action-icon { display: grid; place-items: center; width: 2.35rem; height: 2.35rem; margin-bottom: .8rem; border-radius: .75rem; background: linear-gradient(145deg, #efedff, #e5f9fa); color: #5b4ad6; font-size: .72rem; font-weight: 850; letter-spacing: .05em; }

        .setup-guide { display: flex; align-items: center; gap: .85rem; margin: -.4rem 0 1.15rem; padding: .85rem 1rem; border: 1px solid #e3e6f0; border-radius: 1rem; background: linear-gradient(90deg, rgba(244,242,255,.92), rgba(242,252,252,.82)); }
        .setup-guide-mark { display: grid; place-items: center; width: 2.1rem; height: 2.1rem; border-radius: .7rem; color: #5140c7; background: #e8e4ff; }
        .setup-guide strong, .setup-guide span:not(.setup-guide-mark) { display: block; }
        .setup-guide strong { color: #293454; font-size: .82rem; }
        .setup-guide span:not(.setup-guide-mark) { margin-top: .12rem; color: #6e7893; font-size: .72rem; }
        .question-card-label { display: flex; justify-content: space-between; color: #737e99; font-size: .65rem; font-weight: 800; letter-spacing: .1em; }
        .question-card-label span:last-child { color: #00aab7; }

        .score-ribbon { display: grid; grid-template-columns: 1fr auto minmax(13rem, 1fr); gap: 1.5rem; align-items: center; margin: .45rem 0 1.1rem; padding: 1.1rem 1.35rem; border: 1px solid #dddaf9; border-radius: 1.25rem; color: #fff; background: linear-gradient(115deg, #242257 0%, #5144be 59%, #6d73e9 100%); box-shadow: 0 17px 35px rgba(59,51,157,.15); }
        .score-ribbon span, .score-ribbon strong { display: block; }
        .score-ribbon span { color: #cbd1ff; font-size: .62rem; font-weight: 850; letter-spacing: .1em; }
        .score-ribbon strong { margin-top: .2rem; font-size: 1.25rem; letter-spacing: -.04em; }
        .score-ribbon-number { padding: 0 1.3rem; border-left: 1px solid rgba(255,255,255,.22); border-right: 1px solid rgba(255,255,255,.22); font-size: 2.25rem; font-weight: 850; line-height: 1; letter-spacing: -.09em; }
        .score-ribbon-number small { font-size: .9rem; letter-spacing: 0; }
        .score-ribbon p { margin: 0; color: #e0e3ff !important; font-size: .76rem; line-height: 1.5; }

        @media (max-width: 900px) {
            .dashboard-hero { grid-template-columns: 1fr; gap: 1.2rem; padding: 2rem; }
            .auth-showcase { padding-right: 0; }
            .score-ribbon { grid-template-columns: 1fr auto; }
            .score-ribbon p { grid-column: 1 / -1; }
        }

        @media (max-width: 700px) {
            .auth-topline-note { display: none; }
            .auth-proof { gap: .4rem; margin-top: 1.6rem; }
            .auth-proof > div { min-height: 5.1rem; padding: .65rem; }
            .auth-proof span { font-size: .64rem; }
            .feature-band { grid-template-columns: 1fr; }
            .feature-band > div { border: 0; border-bottom: 1px solid #e8eaf2; padding: .35rem .55rem; }
            .feature-band > div:last-child { border-bottom: 0; }
            .score-ribbon { grid-template-columns: 1fr auto; gap: .9rem; padding: 1rem; }
            .score-ribbon-number { padding: 0 0 0 .9rem; border-right: 0; }
        }

        @media (max-width: 700px) {
            .block-container { padding: 1.2rem 1rem 2.8rem; }
            .dashboard-hero { padding: 1.6rem; }
            .auth-showcase { padding: 1.4rem 0 .8rem; }
            .auth-card { padding: 1.15rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def navigate(page: str) -> None:
    st.session_state.requested_page = page
    st.rerun()


def page_heading(kicker: str, title: str, description: str) -> None:
    """Render a consistent visual heading for authenticated pages."""
    st.markdown(
        f"<div class='page-heading'><div class='eyebrow'>{escape(kicker)}</div>"
        f"<h1>{escape(title)}</h1><p>{escape(description)}</p></div>",
        unsafe_allow_html=True,
    )


def score_label(percentage: float) -> str:
    if percentage >= 85:
        return "Excellent"

    if percentage >= 70:
        return "Strong"

    if percentage >= 50:
        return "Developing"

    return "Needs Practice"
