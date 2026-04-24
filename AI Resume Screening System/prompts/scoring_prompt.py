from langchain_core.prompts import PromptTemplate

SCORING_PROMPT_TEMPLATE = """
You are an expert technical recruiter evaluating a candidate for a specific job description.
Based on the extracted resume data, compare the candidate's skills, tools, and experience with the Job Description.

Job Description:
{job_description}

Extracted Candidate Data:
Skills: {skills}
Experience: {experience}
Tools: {tools}

Instructions:
1. Compare the candidate's extracted data against the job description.
2. Assign a fit score from 0 to 100.
3. Provide a detailed explanation for why this score was assigned.
4. If a candidate lacks core skills (e.g., Python, Machine Learning), the score should reflect that deficiency.
5. Do NOT hallucinate or assume skills that are not explicitly in the candidate data.

Examples:
- If JD requires Python, SQL, and 5 years experience, and Candidate has Python, SQL and 6 years experience -> Score: 90-100. Reason: Matches all core skills and experience.
- If JD requires Python, SQL, and 5 years experience, and Candidate has Python, Java and 2 years experience -> Score: 40-60. Reason: Has some core skills (Python) but lacks SQL and falls short on experience.
- If JD requires Machine Learning, Python, and Candidate has only React, HTML, CSS -> Score: 0-20. Reason: Completely mismatched skill set.

Please output your EvaluationResult exactly as requested.
"""

scoring_prompt = PromptTemplate(
    template=SCORING_PROMPT_TEMPLATE,
    input_variables=["job_description", "skills", "experience", "tools"]
)
