"""
Pydantic Schemas
----------------
These models enforce structured JSON outputs from the LLM chains,
preventing hallucination and ensuring consistent data shapes.
"""

from pydantic import BaseModel, Field
from typing import List


class ExtractedResume(BaseModel):
    """Structured representation of information extracted from a resume."""

    skills: List[str] = Field(
        description=(
            "A list of professional/technical skills extracted from the resume. "
            "Do NOT hallucinate — only include skills explicitly mentioned."
        )
    )
    experience: str = Field(
        description=(
            "A concise summary of the candidate's work experience, "
            "including roles held and total years of experience."
        )
    )
    tools: List[str] = Field(
        description=(
            "A list of software tools, frameworks, or programming languages "
            "explicitly mentioned in the resume."
        )
    )


class EvaluationResult(BaseModel):
    """Structured evaluation result for a resume against a job description."""

    score: int = Field(
        ge=0,
        le=100,
        description="Fit score from 0 to 100 indicating how well the candidate matches the JD.",
    )
    explanation: str = Field(
        description=(
            "A detailed, point-by-point reasoning explaining the score: "
            "what matches, what is missing, and what exceeds expectations."
        )
    )
