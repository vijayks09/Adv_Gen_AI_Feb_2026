"""
AI Resume Screening System - Main Pipeline Orchestrator
=======================================================
Uses Google Gemini (gemini-2.0-flash-lite) -- FREE via Google AI Studio.
Get your free API key at: https://aistudio.google.com/app/apikey

Pipeline:
  Resume -> Skill Extraction -> Matching -> Scoring -> Explanation -> Tracing
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable

from chains.extraction_chain import get_extraction_chain
from chains.scoring_chain import get_scoring_chain

# -- Load environment variables -----------------------------------------------
load_dotenv()


# -- Helpers ------------------------------------------------------------------

def read_file(filepath: str) -> str:
    """Read and return the contents of a text file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


@traceable(name="Resume Screening Pipeline", tags=["resume-screener", "gemini"])
def process_resume(
    resume_path: str,
    job_description: str,
    llm: ChatGoogleGenerativeAI,
    candidate_label: str = ""
) -> dict:
    """
    Full two-step pipeline for a single resume:
      Step 1 -- Extract skills, experience, tools
      Step 2 -- Match against JD, score (0-100), explain
    """
    print(f"\n{'='*60}")
    print(f"  Candidate : {candidate_label}")
    print(f"  Resume    : {resume_path}")
    print(f"{'='*60}")

    resume_text = read_file(resume_path)

    # -- Step 1: Skill Extraction ---------------------------------------------
    extraction_chain = get_extraction_chain(llm)
    print("\n[Step 1] Extracting skills, experience, and tools...")
    extracted = extraction_chain.invoke({"resume_text": resume_text})

    print(f"  Skills    : {', '.join(extracted.skills)}")
    print(f"  Experience: {extracted.experience}")
    print(f"  Tools     : {', '.join(extracted.tools)}")

    # -- Rate limit buffer between steps to avoid 429s ------------------------
    time.sleep(5)

    # -- Step 2: Matching + Scoring + Explanation -----------------------------
    scoring_chain = get_scoring_chain(llm)
    print("\n[Step 2] Scoring against Job Description...")
    evaluation = scoring_chain.invoke({
        "job_description": job_description,
        "skills": ", ".join(extracted.skills),
        "experience": extracted.experience,
        "tools": ", ".join(extracted.tools),
    })

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


# -- Entry Point --------------------------------------------------------------

def main():
    # Validate env
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY is not set.")
        print("  Get your FREE key at: https://aistudio.google.com/app/apikey")
        print("  Then add it to your .env file as: GOOGLE_API_KEY=your_key_here")
        sys.exit(1)

    print("\nAI Resume Screening System")
    print("  Model             : gemini-2.0-flash-lite (FREE)")
    print(f"  LangSmith Tracing : {os.getenv('LANGCHAIN_TRACING_V2', 'false')}")
    print(f"  LangSmith Project : {os.getenv('LANGCHAIN_PROJECT', 'default')}")

    # Initialise Gemini LLM (temperature=0 for deterministic scoring)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    # Load Job Description
    jd_text = read_file("data/jd.txt")
    print("\n[OK] Job Description loaded.\n")

    # -- Define Candidates ----------------------------------------------------
    candidates = [
        ("data/resume_strong.txt",  "Strong Candidate  -- Alice Johnson"),
        ("data/resume_average.txt", "Average Candidate -- Bob Smith"),
        ("data/resume_weak.txt",    "Weak Candidate    -- Charlie Davis"),
    ]

    results = []

    # -- Run Pipeline for Each Candidate --------------------------------------
    for i, (resume_path, label) in enumerate(candidates):
        # Pause between candidates to respect free-tier rate limits (RPM)
        if i > 0:
            print("\n[Rate limit buffer] Waiting 15 seconds before next candidate...")
            time.sleep(15)

        result = process_resume(resume_path, jd_text, llm, label)
        results.append(result)

    # -- Summary Table --------------------------------------------------------
    print(f"\n\n{'='*60}")
    print("  FINAL RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Candidate':<42} {'Score':>5}  Label")
    print(f"  {'-'*56}")
    for r in results:
        print(f"  {r['candidate']:<42} {r['score']:>5}/100  {r['label']}")

    # -- Save JSON Results ----------------------------------------------------
    output_path = "results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Detailed results saved -> {output_path}")
    print("[OK] Check LangSmith dashboard -> https://smith.langchain.com")


if __name__ == "__main__":
    main()
