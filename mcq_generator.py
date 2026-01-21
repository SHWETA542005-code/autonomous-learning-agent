import json
from config import llm


def generate_mcqs(context, num_questions=5):
    """
    Generates MCQs strictly in JSON format.
    """

    prompt = f"""
You are an expert educator.

Based ONLY on the content below, generate {num_questions} MCQs.

CONTENT:
{context}

STRICT RULES:
- Output ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include any text outside JSON

JSON FORMAT:
[
  {{
    "question": "question text",
    "options": {{
      "A": "option A",
      "B": "option B",
      "C": "option C",
      "D": "option D"
    }},
    "correct_answer": "A"
  }}
]
"""

    response = llm.invoke(prompt)

    raw = response.content.strip()

    try:
        mcqs = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM did not return valid JSON.\n\nRAW OUTPUT:\n{raw}"
        ) from e

    return mcqs


def ask_questions(questions):
    """
    Streamlit / CLI compatible answer collector.
    This function will be UI-controlled in Streamlit.
    """
    user_answers = []

    for q in questions:
        user_answers.append(None)

    return user_answers
