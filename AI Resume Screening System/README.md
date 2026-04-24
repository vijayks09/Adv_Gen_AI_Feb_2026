# AI Resume Screening System

An AI-powered Resume Screening System built with **LangChain**, **Google Gemini**, and **LangSmith**.

## Live Demo
[AI Resume Screener - Live App](#) ← Deploy to Render and paste URL here

## Features
- **Skill Extraction** — Extracts skills, experience, and tools from any resume
- **JD Matching** — Compares candidate against a Job Description
- **AI Scoring (0-100)** — Assigns a fit score with detailed explanation
- **3 Sample Candidates** — Strong / Average / Weak pre-loaded for testing
- **LangSmith Tracing** — Full pipeline visibility
- **Web Portal** — Beautiful dark-themed dashboard

## Pipeline Architecture
```
Resume → Extract (LangChain LCEL) → Match → Score → Explain → Display
```

## Tech Stack
- Python 3.11
- LangChain (LCEL, PromptTemplate, with_structured_output)
- Google Gemini 2.0 Flash (free tier)
- LangSmith (tracing)
- Flask + Gunicorn
- Pydantic v2

## Project Structure
```
ai-resume-screener/
├── app.py                  # Flask web application
├── main.py                 # CLI pipeline runner
├── demo.py                 # Demo mode runner
├── requirements.txt
├── Procfile                # For Render/Heroku
├── render.yaml             # Render deployment config
├── data/
│   ├── jd.txt              # Job Description
│   ├── resume_strong.txt   # Strong candidate
│   ├── resume_average.txt  # Average candidate
│   └── resume_weak.txt     # Weak candidate
├── models/
│   └── schemas.py          # Pydantic output schemas
├── prompts/
│   ├── extraction_prompt.py
│   └── scoring_prompt.py
├── chains/
│   ├── extraction_chain.py
│   └── scoring_chain.py
└── templates/
    └── index.html          # Web portal
```

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-screener.git
cd ai-resume-screener
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
cp .env.example .env
# Edit .env and add your keys:
# GOOGLE_API_KEY=your_free_key_from_aistudio.google.com
```

### 4. Run locally
```bash
python app.py        # Web portal at http://localhost:5000
python main.py       # CLI runner
python demo.py       # Demo mode (no API key needed)
```

## Deploy to Render (Free)
1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Add env variable: `GOOGLE_API_KEY=your_key`
5. Click Deploy — done!

## Evaluation Results (Sample)
| Candidate | Score | Verdict |
|---|---|---|
| Alice Johnson (Strong) | 91/100 | Strong Fit |
| Bob Smith (Average) | 54/100 | Average Fit |
| Charlie Davis (Weak) | 12/100 | Weak Fit |
