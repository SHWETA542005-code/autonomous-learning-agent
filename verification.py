from config import llm

def score_answers(questions: list, answers: list, context: str) -> float:
    prompt = f"""
You are grading answers.

Context:
{context}

Questions and Answers:
"""

    for q, a in zip(questions, answers):
        prompt += f"\nQ: {q}\nA: {a}\n"

    prompt += """
Give a score from 0 to 100 representing understanding.
ONLY return the number.
"""

    score_text = llm.invoke(prompt).content.strip()

    try:
        return float(score_text) / 100
    except:
        return 0.0
