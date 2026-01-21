from config import llm

def feynman_explain(questions, user_answers):
    explanations = []

    for q, user_ans in zip(questions, user_answers):
        if user_ans != q["correct_answer"]:
            prompt = f"""
Question:
{q['question']}

User Answer: {user_ans}
Correct Answer: {q['correct_answer']}

Explain in:
1. Very simple words
2. One clear analogy

Keep it short.
"""
            response = llm.invoke(prompt)
            explanations.append({
                "question": q["question"],
                "user_answer": user_ans,
                "correct_answer": q["correct_answer"],
                "explanation": response.content
            })

    return explanations
