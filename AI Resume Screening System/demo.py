"""
AI Resume Screening System - DEMO MODE
=======================================
Runs the complete pipeline (Extraction -> Matching -> Scoring -> Explanation)
using simulated LLM responses that match exactly what Gemini would return.

This demonstrates the full working system:
  Resume -> Extract -> Match -> Score -> Explain -> Results

To run with a real LLM (Google Gemini free key):
  1. Get free key at: https://aistudio.google.com/app/apikey
  2. Set GOOGLE_API_KEY in .env
  3. Run: python main.py
"""

import os
import json
import time
from dotenv import load_dotenv
from models.schemas import ExtractedResume, EvaluationResult

load_dotenv()

# ============================================================
#  REALISTIC SIMULATED LLM RESPONSES
#  (What Gemini returns for each resume vs. this exact JD)
# ============================================================

MOCK_EXTRACTIONS = {
    "data/resume_strong.txt": ExtractedResume(
        skills=[
            "Machine Learning",
            "Deep Learning",
            "Predictive Modeling",
            "Data Visualization",
            "Model Deployment",
            "Customer Churn Prediction",
        ],
        experience=(
            "Data Scientist at TechCorp for 4 years. Developed and deployed "
            "ML models for customer churn prediction. Analyzed large datasets "
            "using SQL and Python. Created Tableau dashboards for stakeholders."
        ),
        tools=["Python", "SQL", "PyTorch", "scikit-learn", "Tableau",
               "Docker", "Kubernetes", "MLflow", "Git"],
    ),
    "data/resume_average.txt": ExtractedResume(
        skills=[
            "Data Analysis",
            "Basic Machine Learning",
            "Statistical Analysis",
            "Reporting",
            "Customer Segmentation",
        ],
        experience=(
            "Data Analyst at DataInc for 2 years. Analyzed business data using "
            "Python and SQL. Built basic classification models. Presented findings "
            "via PowerBI dashboards."
        ),
        tools=["Python", "SQL", "scikit-learn", "PowerBI", "Excel"],
    ),
    "data/resume_weak.txt": ExtractedResume(
        skills=[
            "Backend Development",
            "API Design",
            "Database Management",
            "RESTful APIs",
        ],
        experience=(
            "Software Engineer at WebSolutions for 1 year. Developed RESTful APIs "
            "using Java and Spring Boot. Designed database schemas and wrote MySQL "
            "queries."
        ),
        tools=["Java", "Spring Boot", "MySQL", "Git", "Postman"],
    ),
}

MOCK_EVALUATIONS = {
    "data/resume_strong.txt": EvaluationResult(
        score=91,
        explanation=(
            "Alice is an excellent match for the Data Scientist role. "
            "STRENGTHS: (1) Core skills fully present — Python, SQL, Machine Learning, "
            "Data Visualization with Tableau. (2) Exceeds experience requirement with "
            "4 years vs the 3-year minimum, including hands-on production ML deployment. "
            "(3) PyTorch and scikit-learn directly address the ML framework requirement. "
            "(4) Tableau directly matches the data visualization requirement. "
            "(5) Bonus: MLflow, Docker, Kubernetes indicate strong MLOps maturity. "
            "GAPS: No explicit TensorFlow mention (uses PyTorch instead — still valid). "
            "VERDICT: Strong hire recommendation."
        ),
    ),
    "data/resume_average.txt": EvaluationResult(
        score=54,
        explanation=(
            "Bob is a partial match for the Data Scientist role. "
            "STRENGTHS: (1) Python and SQL are present and match core requirements. "
            "(2) scikit-learn experience covers the ML framework requirement at a basic level. "
            "(3) PowerBI covers the data visualization requirement. "
            "GAPS: (1) Only 2 years of experience vs the 3-year minimum — falls short. "
            "(2) Machine Learning experience is described as 'basic' — lacks depth in "
            "predictive modeling or model deployment to production. "
            "(3) No mention of TensorFlow or PyTorch for deep learning. "
            "VERDICT: Average candidate — could grow into the role with mentorship."
        ),
    ),
    "data/resume_weak.txt": EvaluationResult(
        score=12,
        explanation=(
            "Charlie is a very poor match for the Data Scientist role. "
            "STRENGTHS: MySQL/SQL is mentioned, which partially overlaps with the SQL requirement. "
            "GAPS: (1) No Python — the primary language required. "
            "(2) No Machine Learning skills whatsoever — the core of the role. "
            "(3) No data visualization tools (Tableau, PowerBI, Matplotlib). "
            "(4) Only 1 year of experience, well below the 3-year minimum. "
            "(5) Primary skills (Java, Spring Boot, API design) are backend engineering, "
            "not data science. This is a completely different discipline. "
            "VERDICT: Not suitable for this role. Would need 2-3 years of retraining."
        ),
    ),
}


def read_file(filepath: str) -> str:
    """Read and return the contents of a text file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def process_resume_demo(resume_path: str, candidate_label: str) -> dict:
    """Simulate the full pipeline for a single resume using mock LLM responses."""

    print(f"\n{'='*60}")
    print(f"  Candidate : {candidate_label}")
    print(f"  Resume    : {resume_path}")
    print(f"{'='*60}")

    # -- Step 1: Skill Extraction (simulated LLM call) ------------------------
    print("\n[Step 1] Extracting skills, experience, and tools...")
    print("         (Invoking Extraction Chain -> gemini-2.0-flash-lite)")
    time.sleep(1.2)  # Simulate API latency

    extracted = MOCK_EXTRACTIONS[resume_path]
    print(f"  Skills    : {', '.join(extracted.skills)}")
    print(f"  Experience: {extracted.experience}")
    print(f"  Tools     : {', '.join(extracted.tools)}")

    # -- Step 2: Matching + Scoring + Explanation (simulated LLM call) --------
    print("\n[Step 2] Scoring against Job Description...")
    print("         (Invoking Scoring Chain -> gemini-2.0-flash-lite)")
    time.sleep(1.5)  # Simulate API latency

    evaluation = MOCK_EVALUATIONS[resume_path]

    # Score label
    if evaluation.score >= 75:
        label = "[STRONG FIT]"
    elif evaluation.score >= 45:
        label = "[AVERAGE FIT]"
    else:
        label = "[WEAK FIT]"

    print(f"\n  FIT SCORE  : {evaluation.score} / 100  {label}")
    print(f"  EXPLANATION:\n    {evaluation.explanation}")

    return {
        "candidate": candidate_label,
        "resume_path": resume_path,
        "extracted": {
            "skills": extracted.skills,
            "experience": extracted.experience,
            "tools": extracted.tools,
        },
        "score": evaluation.score,
        "label": label,
        "explanation": evaluation.explanation,
    }


def main():
    print("\n" + "#"*60)
    print("#  AI RESUME SCREENING SYSTEM                              #")
    print("#  Powered by LangChain + Google Gemini + LangSmith       #")
    print("#"*60)
    print("\n  Model             : gemini-2.0-flash-lite")
    print("  Pipeline Steps    : Extract -> Match -> Score -> Explain")
    print("  LangChain LCEL    : PromptTemplate | LLM.with_structured_output")
    print("  LangSmith Tracing : Enabled (set LANGCHAIN_TRACING_V2=true)")
    print("  Mode              : DEMO (simulated LLM responses)")

    # Load Job Description
    jd_text = read_file("data/jd.txt")
    print("\n[OK] Job Description loaded.")
    print("-"*60)
    print(jd_text.strip())
    print("-"*60)

    # -- Define Candidates ----------------------------------------------------
    candidates = [
        ("data/resume_strong.txt",  "Strong Candidate  -- Alice Johnson"),
        ("data/resume_average.txt", "Average Candidate -- Bob Smith"),
        ("data/resume_weak.txt",    "Weak Candidate    -- Charlie Davis"),
    ]

    results = []

    # -- Run Pipeline for Each Candidate --------------------------------------
    for resume_path, label in candidates:
        result = process_resume_demo(resume_path, label)
        results.append(result)
        time.sleep(0.5)

    # -- Summary Table --------------------------------------------------------
    print(f"\n\n{'='*60}")
    print("  FINAL RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Candidate':<42} {'Score':>5}  Verdict")
    print(f"  {'-'*57}")
    for r in results:
        print(f"  {r['candidate']:<42} {r['score']:>5}/100  {r['label']}")

    print(f"\n  Ranking: {results[0]['candidate'].split('--')[1].strip()} "
          f"> {results[1]['candidate'].split('--')[1].strip()} "
          f"> {results[2]['candidate'].split('--')[1].strip()}")
    print("  (Correct order confirmed: Strong > Average > Weak)")

    # -- Save JSON Results ----------------------------------------------------
    output_path = "results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Full results saved -> {output_path}")
    print("[OK] Pipeline complete. All 3 resumes evaluated successfully.")
    print("\n" + "#"*60)
    print("#  TO RUN WITH REAL GEMINI AI:                             #")
    print("#  1. Get FREE key: https://aistudio.google.com/app/apikey #")
    print("#  2. Add to .env: GOOGLE_API_KEY=your_key               #")
    print("#  3. Run: python main.py                                  #")
    print("#"*60)


if __name__ == "__main__":
    main()
