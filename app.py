import streamlit as st
from curriculum import checkpoints
from teaching import teach
from mcq_generator import generate_mcqs
from evaluation import evaluate_answers
from feynman import feynman_explain

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Autonomous Learning Agent",
    layout="centered",
    initial_sidebar_state="collapsed"
)

TOTAL_CHECKPOINTS = len(checkpoints)

# -------------------------------------------------
# THEME (BLACK + GREEN)
# -------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #ffffff;
}

header, footer {visibility: hidden;}
section[data-testid="stSidebar"] {display: none;}

h1, h2, h3 {
    text-align: center;
    color: white;
}

.card {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1.2rem;
}

/* Radio alignment fix */
div[role="radiogroup"] label {
    display: flex !important;
    align-items: center;
    gap: 12px;
    background: rgba(255,255,255,0.06);
    padding: 12px 14px;
    border-radius: 10px;
    margin: 8px 0;
}

div[role="radiogroup"] label:hover {
    background: rgba(16, 185, 129, 0.18);
}

.stButton button {
    display: block;
    margin: 1.2rem auto;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: black;
    font-weight: 600;
    border-radius: 10px;
    padding: 0.6rem 2rem;
}

[data-testid="stMetric"] {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SESSION INIT
# -------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "dashboard"
    st.session_state.checkpoint_index = 0

# -------------------------------------------------
# PROGRESS BAR (GLOBAL)
# -------------------------------------------------
progress = st.session_state.checkpoint_index / TOTAL_CHECKPOINTS
st.progress(progress)

st.markdown(
    f"<p style='text-align:center;'>Progress: {int(progress * 100)}%</p>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# FINAL COMPLETION
# -------------------------------------------------
if st.session_state.checkpoint_index >= TOTAL_CHECKPOINTS:
    st.balloons()

    st.title("🎓 Learning Completed")

    st.markdown("""
    <div class="card" style="text-align:center;">
        <h3>You have successfully completed all learning checkpoints.</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Restart Learning"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.stop()

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
if st.session_state.stage == "dashboard":
    st.title("🚀 Autonomous Learning Agent")
    st.subheader("Learn → Test → Explain → Master")

    selected = st.selectbox(
        "Choose a checkpoint",
        options=list(range(TOTAL_CHECKPOINTS)),
        format_func=lambda i: checkpoints[i]["title"]
    )

    if st.button("▶ Start Learning"):
        st.session_state.checkpoint_index = selected
        st.session_state.stage = "teach"
        st.rerun()

# -------------------------------------------------
# TEACH
# -------------------------------------------------
elif st.session_state.stage == "teach":
    checkpoint = checkpoints[st.session_state.checkpoint_index]

    st.title(checkpoint["title"])

    context = teach({"checkpoint": checkpoint})["context"]
    st.session_state.context = context

    st.markdown(f'<div class="card">{context}</div>', unsafe_allow_html=True)

    if st.button("📝 Start Quiz"):
        st.session_state.questions = generate_mcqs(context)
        st.session_state.stage = "quiz"
        st.rerun()

# -------------------------------------------------
# QUIZ
# -------------------------------------------------
elif st.session_state.stage == "quiz":
    st.title("🧠 Knowledge Check")

    user_answers = []

    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"""
        <div class="card">
            <b>Q{i+1}. {q['question']}</b>
        </div>
        """, unsafe_allow_html=True)

        ans = st.radio(
            "",
            options=list(q["options"].keys()),
            format_func=lambda x: f"{x}. {q['options'][x]}",
            key=f"q_{i}"
        )
        user_answers.append(ans)

    if st.button("✅ Submit"):
        st.session_state.user_answers = user_answers
        result = evaluate_answers(
            st.session_state.questions,
            user_answers,
            st.session_state.context
        )
        st.session_state.result = result
        st.session_state.stage = "next" if result["passed"] else "feynman"
        st.rerun()

# -------------------------------------------------
# FEYNMAN
# -------------------------------------------------
elif st.session_state.stage == "feynman":
    st.title("🧠 Let’s Fix the Gaps")

    explanations = feynman_explain(
        st.session_state.questions,
        st.session_state.user_answers
    )

    for e in explanations:
        st.markdown(f"""
        <div class="card">
            <b>{e['question']}</b><br><br>
            ❌ Your Answer: <b>{e['user_answer']}</b><br>
            ✅ Correct Answer: <b>{e['correct_answer']}</b><br><br>
            {e['explanation']}
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔁 Retry Quiz"):
        st.session_state.stage = "quiz"
        st.rerun()

# -------------------------------------------------
# CHECKPOINT COMPLETED
# -------------------------------------------------
elif st.session_state.stage == "next":
    st.balloons()

    r = st.session_state.result

    st.title("✅ Checkpoint Completed")

    st.metric("Score", f"{r['score']} / {r['total']}")
    st.metric("Percentage", f"{r['percentage']}%")

    if st.button("➡ Continue"):
        st.session_state.checkpoint_index += 1
        st.session_state.stage = "teach"
        st.rerun()
