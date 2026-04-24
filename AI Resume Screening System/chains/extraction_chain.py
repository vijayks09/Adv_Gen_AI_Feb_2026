"""
Extraction Chain
----------------
LCEL chain: resume text → ExtractedResume (skills, experience, tools)
Uses Google Gemini via ChatGoogleGenerativeAI.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from prompts.extraction_prompt import extraction_prompt
from models.schemas import ExtractedResume


def get_extraction_chain(llm: ChatGoogleGenerativeAI):
    """
    Build the extraction LCEL chain.
    Prompt → LLM (with_structured_output) → ExtractedResume
    """
    structured_llm = llm.with_structured_output(ExtractedResume)
    chain = extraction_prompt | structured_llm
    return chain
