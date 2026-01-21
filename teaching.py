from config import llm


def teach(state):
    """
    Teaching node.
    Generates explanation for the current checkpoint topic.

    This function is SAFE to use in:
    - LangGraph execution
    - Streamlit UI
    """

    # Mandatory
    checkpoint = state.get("checkpoint")
    if checkpoint is None:
        raise ValueError("State must contain 'checkpoint'")

    topic = checkpoint.get("title", "Unknown Topic")
    objectives = checkpoint.get("objectives", [])

    # Optional (LangGraph-only, safe defaults for Streamlit)
    checkpoint_index = state.get("checkpoint_index", 0)
    total_checkpoints = state.get("total_checkpoints", "?")

    prompt = f"""
You are an expert AI teacher.

Teach the topic: {topic}

Learning objectives:
{objectives}

Explain clearly, simply, and structurally.
Use headings and bullet points.
Do NOT ask questions.
"""

    response = llm.invoke(prompt)

    # Console output (for CLI runs)
    print("\n" + "=" * 80)
    print(f"📍 CHECKPOINT {checkpoint_index + 1} / {total_checkpoints}")
    print(f"📌 TOPIC: {topic}")
    print("=" * 80)
    print(response.content)

    # Store generated context for next nodes
    state["context"] = response.content

    return state
