"""
AI Resume Screening System - Flask Web Application (Production)
===============================================================
"""

import os
import json
import time
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from models.schemas import ExtractedResume, EvaluationResult
from chains.extraction_chain import get_extraction_chain
from chains.scoring_chain import get_scoring_chain

load_dotenv()

app = Flask(__name__)

# ── File paths (robust for production) ───────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _read(filename):
    with open(os.path.join(BASE_DIR, "data", filename), encoding="utf-8") as f:
        return f.read().strip()

DEFAULT_JD = _read("jd.txt")
DEFAULT_RESUMES = {
    "strong":  _read("resume_strong.txt"),
    "average": _read("resume_average.txt"),
    "weak":    _read("resume_weak.txt"),
}

# ── Pre-computed demo results (Gemini-quality) ────────────────────────────────
DEMO_RESULTS = {
    "strong": {
        "extracted": {
            "skills": ["Machine Learning", "Deep Learning", "Predictive Modeling",
                       "Data Visualization", "Model Deployment", "Customer Churn Prediction"],
            "experience": "Data Scientist at TechCorp for 4 years. Developed and deployed ML models for customer churn prediction. Analyzed large datasets using SQL and Python. Created Tableau dashboards for stakeholders.",
            "tools": ["Python", "SQL", "PyTorch", "scikit-learn", "Tableau", "Docker", "Kubernetes", "MLflow", "Git"],
        },
        "score": 91, "label": "Strong Fit", "color": "green",
        "explanation": (
            "Alice is an excellent match for the Data Scientist role. "
            "STRENGTHS: (1) Core skills fully present — Python, SQL, Machine Learning, "
            "Data Visualization with Tableau. (2) Exceeds the 3-year experience requirement "
            "with 4 years including production ML deployment. (3) PyTorch and scikit-learn "
            "directly address the ML framework requirement. (4) Bonus: MLflow, Docker, "
            "Kubernetes demonstrate strong MLOps maturity beyond what the JD requires. "
            "GAPS: No explicit TensorFlow mention — uses PyTorch instead, which is equally valid. "
            "VERDICT: Strong hire recommendation."
        ),
        "mode": "demo",
    },
    "average": {
        "extracted": {
            "skills": ["Data Analysis", "Basic Machine Learning", "Statistical Analysis",
                       "Reporting", "Customer Segmentation"],
            "experience": "Data Analyst at DataInc for 2 years. Analyzed business data using Python and SQL. Built basic classification models. Presented findings via PowerBI dashboards.",
            "tools": ["Python", "SQL", "scikit-learn", "PowerBI", "Excel"],
        },
        "score": 54, "label": "Average Fit", "color": "yellow",
        "explanation": (
            "Bob is a partial match for the Data Scientist role. "
            "STRENGTHS: (1) Python and SQL are present and match core requirements. "
            "(2) scikit-learn covers the ML framework requirement at a basic level. "
            "(3) PowerBI covers the data visualization requirement. "
            "GAPS: (1) Only 2 years of experience vs the 3-year minimum. "
            "(2) ML experience is 'basic' — lacks production deployment depth. "
            "(3) No TensorFlow or PyTorch mentioned. "
            "VERDICT: Average candidate — could grow into the role with mentorship."
        ),
        "mode": "demo",
    },
    "weak": {
        "extracted": {
            "skills": ["Backend Development", "API Design", "Database Management", "RESTful APIs"],
            "experience": "Software Engineer at WebSolutions for 1 year. Developed RESTful APIs using Java and Spring Boot. Designed MySQL database schemas.",
            "tools": ["Java", "Spring Boot", "MySQL", "Git", "Postman"],
        },
        "score": 12, "label": "Weak Fit", "color": "red",
        "explanation": (
            "Charlie is a very poor match for the Data Scientist role. "
            "STRENGTHS: MySQL/SQL partially overlaps with the SQL requirement. "
            "GAPS: (1) No Python — the primary language required. "
            "(2) No Machine Learning skills — the core of the role. "
            "(3) No data visualization tools (Tableau/PowerBI/Matplotlib). "
            "(4) Only 1 year of experience, well below the 3-year minimum. "
            "(5) Primary skills (Java, Spring Boot, API) are backend engineering, not data science. "
            "VERDICT: Not suitable. Would need 2-3 years of retraining to qualify."
        ),
        "mode": "demo",
    },
}


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite", temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )


def run_pipeline(resume_text: str, jd_text: str) -> dict:
    """LangChain LCEL pipeline: Extract -> Score."""
    llm = get_llm()
    extraction_chain = get_extraction_chain(llm)
    extracted = extraction_chain.invoke({"resume_text": resume_text})
    time.sleep(3)
    scoring_chain = get_scoring_chain(llm)
    evaluation = scoring_chain.invoke({
        "job_description": jd_text,
        "skills": ", ".join(extracted.skills),
        "experience": extracted.experience,
        "tools": ", ".join(extracted.tools),
    })
    if evaluation.score >= 75:
        label, color = "Strong Fit", "green"
    elif evaluation.score >= 45:
        label, color = "Average Fit", "yellow"
    else:
        label, color = "Weak Fit", "red"
    return {
        "extracted": {"skills": extracted.skills, "experience": extracted.experience, "tools": extracted.tools},
        "score": evaluation.score, "label": label, "color": color,
        "explanation": evaluation.explanation, "mode": "live",
    }


def detect_sample(resume_text: str):
    for key, text in DEFAULT_RESUMES.items():
        if resume_text[:80] == text[:80]:
            return key
    return None


@app.route("/")
def index():
    return render_template("index.html", default_jd=DEFAULT_JD, default_resumes=DEFAULT_RESUMES)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    resume_text = data.get("resume", "").strip()
    jd_text     = data.get("jd", DEFAULT_JD).strip()
    force_demo  = data.get("demo", False)

    if not resume_text:
        return jsonify({"error": "Resume text is required."}), 400

    if force_demo:
        key = detect_sample(resume_text) or "strong"
        time.sleep(1)
        return jsonify(DEMO_RESULTS[key])

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        key = detect_sample(resume_text) or "strong"
        result = dict(DEMO_RESULTS[key])
        result["quota_note"] = "No API key configured — showing pre-computed output."
        return jsonify(result)

    try:
        return jsonify(run_pipeline(resume_text, jd_text))
    except Exception as e:
        err = str(e)
        if "RESOURCE_EXHAUSTED" in err or "429" in err:
            key = detect_sample(resume_text) or "strong"
            result = dict(DEMO_RESULTS[key])
            result["quota_note"] = "API quota exceeded — showing pre-computed Gemini output."
            return jsonify(result)
        return jsonify({"error": err}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    print(f"\nAI Resume Screening System - Web Portal")
    print(f"  Open: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
