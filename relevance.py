from config import llm
import json

def compute_relevance(context: str, objectives: list) -> float:
    """
    Computes relevance score (0–100) between teaching context and objectives
    """

    prompt = f"""
You are an evaluator.

Given:
LEARNING OBJECTIVES:
{objectives}

TEACHING CONTENT:
{context}

Evaluate how well the teaching content covers the objectives.

Return ONLY valid JSON in this format:
{{
  "relevance_score": number
}}

Score from 0 to 100.
"""

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)
        return float(result["relevance_score"])
    except Exception:
        return 0.0
