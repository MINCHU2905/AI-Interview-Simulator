# InterviewAce AI

InterviewAce AI is an AI-powered interview simulator for students and early-career candidates. It reads a PDF resume, generates tailored interview questions, evaluates written answers, and keeps a history of performance over time.

## Features

- Secure registration and login with bcrypt password hashes
- PDF resume upload and text extraction with PyMuPDF
- Resume analysis for skills, projects, education, strengths, and growth opportunities
- Personalized HR, Technical, Python, AI/ML, Data Science, and custom interviews
- Difficulty and question-count controls
- One-question-at-a-time interview flow with persisted responses
- Per-answer scoring, feedback, missing points, suggested answers, and improvement tips
- Final report with question-level scores and improvement areas
- Dashboard metrics and Plotly performance analytics
- SQLite persistence for users, resumes, interviews, and questions

## Quick start

1. Create and activate a virtual environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`, then add your Gemini API key.

   ```powershell
   Copy-Item .env.example .env
   ```

4. Run the app.

   ```powershell
   streamlit run app.py
   ```

The database is created automatically at `database/interview.db`. Uploaded resumes are saved beneath `uploads/` in user-specific folders.

## Gemini configuration

Set `GEMINI_API_KEY` in `.env` to enable live resume analysis, question generation, and answer evaluation. The app uses the current Google GenAI SDK with `gemini-2.5-flash` by default; set `GEMINI_MODEL` if you need a supported alternative.

Without a key, the app remains usable in development mode: it identifies common skills locally, uses a curated interview-question bank, and marks heuristic answer reviews clearly in the feedback.

## Project layout

```text
InterviewAce AI/
├── app.py                 # Streamlit entry point and authenticated pages
├── auth.py                # bcrypt registration and login helpers
├── database.py            # SQLite schema and queries
├── resume_parser.py       # PDF validation, storage, and PyMuPDF extraction
├── ai_service.py          # Gemini prompts plus development fallback
├── interview.py           # Setup and interview session UI
├── report.py              # Final interview report UI
├── dashboard.py           # Dashboard and analytics UI
├── utils.py               # Shared UI/data helpers
├── config.py              # Paths and environment configuration
├── prompts/               # Versionable AI prompt templates
├── database/              # Runtime SQLite database
└── uploads/               # User-uploaded resumes
```

## Data model

- `users`: account details and bcrypt password hash
- `resumes`: uploaded file metadata, extracted text, and resume analysis
- `interviews`: selected settings, final score, percentage, and summary
- `questions`: generated question, candidate answer, score, and structured feedback

## Notes

- Upload only text-based PDF resumes; scanned PDFs need OCR before they can be parsed.
- The app is designed for local development. Before deploying, add CSRF/session hardening, a managed database, encrypted object storage, and a document-retention policy appropriate for your users.
