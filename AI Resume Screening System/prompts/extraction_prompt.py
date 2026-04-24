from langchain_core.prompts import PromptTemplate

EXTRACTION_PROMPT_TEMPLATE = """
You are an expert technical recruiter and resume parser. 
Your task is to extract relevant information from the provided resume text.

Instructions:
1. Extract a clear list of skills mentioned in the resume.
2. Summarize the candidate's work experience and total years of experience.
3. Extract a list of specific tools and programming languages mentioned.
4. IMPORTANT RULE: Do NOT hallucinate. Do NOT assume skills, tools, or experience that are not explicitly present in the resume text.

Resume Text:
{resume_text}
"""

extraction_prompt = PromptTemplate(
    template=EXTRACTION_PROMPT_TEMPLATE,
    input_variables=["resume_text"]
)
