from relevance import compute_relevance

def evaluate_answers(questions, user_answers, context, pass_percentage=70):
    correct = 0

    for q, ans in zip(questions, user_answers):
        if ans == q["correct_answer"]:
            correct += 1

    total = len(questions)
    percentage = (correct / total) * 100
    passed = percentage >= pass_percentage

    relevance_score = compute_relevance(context, questions)

    return {
        "score": correct,
        "total": total,
        "percentage": percentage,
        "passed": passed,
        "relevance_score": relevance_score
    }
