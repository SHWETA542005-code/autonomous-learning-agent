from langgraph.graph import StateGraph, END

from curriculum import checkpoints
from teaching import teach
from mcq_generator import generate_mcqs, ask_questions
from evaluation import evaluate
from feynman import feynman_explain


def teaching_node(state):
    idx = state["checkpoint_index"]
    checkpoint = checkpoints[idx]

    state["checkpoint"] = checkpoint
    state = teach(state)
    return state


def quiz_node(state):
    questions = generate_mcqs(state["context"])
    user_answers = ask_questions(questions)

    state["questions"] = questions
    state["user_answers"] = user_answers
    return state


def evaluation_node(state):
    return evaluate(state, pass_percentage=70)


def progress_node(state):
    """
    ONLY job: move to next checkpoint
    """
    state["checkpoint_index"] += 1
    return state


def decision_node(state):
    """
    ONLY decides where to go
    """
    if state["passed"]:
        if state["checkpoint_index"] + 1 >= state["total_checkpoints"]:
            return END
        return "progress"
    else:
        return "feynman"


def build_graph():
    graph = StateGraph(dict)

    graph.add_node("teach", teaching_node)
    graph.add_node("quiz", quiz_node)
    graph.add_node("evaluate", evaluation_node)
    graph.add_node("feynman", feynman_explain)
    graph.add_node("progress", progress_node)

    graph.set_entry_point("teach")

    graph.add_edge("teach", "quiz")
    graph.add_edge("quiz", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        decision_node
    )

    graph.add_edge("progress", "teach")
    graph.add_edge("feynman", "quiz")

    return graph.compile()
