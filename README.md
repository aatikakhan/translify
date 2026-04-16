# Translify - GenAI-Based PDF Language Translator

Translify is a cloud-based web application that translates uploaded PDF documents from multiple languages to English using Gemini API. The app is designed for CCL Mini Project evaluation with deployable AWS architecture using EC2, S3, and RDS.

## Features

- User registration and login
- PDF upload and storage
- Text extraction from uploaded PDF
- Gemini-powered translation to English
- Translated PDF generation and download
- Translation history tracking
- AWS-ready architecture (EC2 + S3 + RDS)
- Local storage mode for easy testing without cloud credentials

## Architecture

- **Frontend + Backend:** FastAPI app deployed on Amazon EC2
- **File Storage:** Amazon S3 (`originals/` and `translated/`)
- **Database:** Amazon RDS (MySQL/PostgreSQL via `DATABASE_URL`)
- **Translation Engine:** Gemini API

## Local Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create environment file:

   ```bash
   cp .env.example .env
   ```

4. Update `.env` values. For local demo:
   - Keep `USE_LOCAL_STORAGE=true`
   - Use SQLite by setting:
     - `DATABASE_URL=sqlite:///./translify_dev.db`
   - Add your `GEMINI_API_KEY`

5. Run app:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open:
   - <http://127.0.0.1:8000>

## Production Setup on AWS

See `deploy/DEPLOYMENT.md` for full EC2 + S3 + RDS deployment steps.

## Database Tables

- `users`
- `documents`

## Demo Checklist

- Register/Login user
- Upload non-English PDF
- Translate with Gemini
- Download translated PDF
- Show file objects in S3
- Show metadata records in RDS

## Project Submission

- Source code folder: this repository
- Report files:
  - `docs/report/Translify_Report.tex`
  - `docs/report/Translify_Report.doc`
