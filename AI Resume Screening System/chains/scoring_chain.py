"""
Scoring Chain
-------------
LCEL chain: extracted data + JD → EvaluationResult (score + explanation)
Uses Google Gemini via ChatGoogleGenerativeAI.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from prompts.scoring_prompt import scoring_prompt
from models.schemas import EvaluationResult


def get_scoring_chain(llm: ChatGoogleGenerativeAI):
    """
    Build the scoring LCEL chain.
    Prompt → LLM (with_structured_output) → EvaluationResult
    """
    structured_llm = llm.with_structured_output(EvaluationResult)
    chain = scoring_prompt | structured_llm
    return chain
