import streamlit as st
from curriculum import checkpoints
from teaching import teach
from mcq_generator import generate_mcqs
from evaluation import evaluate_answers
from feynman import feynman_explain
from db import (
    init_db,
    create_user,
    authenticate_user,
    save_checkpoint_performance,
    fetch_checkpoint_history,
    fetch_overall_stats
)



# -------------------------------------------------
# INIT DB
# -------------------------------------------------
init_db()

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Autonomous Learning Agent",
    layout="centered",
)

TOTAL_CHECKPOINTS = len(checkpoints)

st.markdown("""
<style>
.history-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 14px;
}

.history-title {
    font-size: 1.1rem;
    font-weight: 600;
}

.history-status {
    font-size: 0.95rem;
    margin-top: 4px;
}

.history-meta {
    font-size: 0.8rem;
    opacity: 0.7;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.feynman-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 18px;

}

.feynman-question {
    font-weight: 600;
    font-size: 1.05rem;
    margin-bottom: 12px;
}



.feynman-answer.wrong {
    color: #ff6b6b;
}

.feynman-answer.correct {
    color: #51cf66;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# SESSION INIT
# -------------------------------------------------
if "nav" not in st.session_state:
    st.session_state.nav = "Home"

if "stage" not in st.session_state:
    st.session_state.stage = None

if "checkpoint_index" not in st.session_state:
    st.session_state.checkpoint_index = 0

if "user_id" not in st.session_state:
    st.session_state.user_id = None

USER_ID = st.session_state.user_id


if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"  # or signup


# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
st.sidebar.title("🚀 Autonomous Agent")

st.session_state.nav = st.sidebar.radio(
    "Navigation",
    ["Home", "Overall Performance", "Checkpoint History"]
)

# -------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------
if st.session_state.user_id is None:
    st.title("🔐 Autonomous Learning Agent")

    choice = st.radio(
        "Select option",
        ["Login", "Sign Up"],
        horizontal=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Login":
        if st.button("Login"):
            user_id = authenticate_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:  # Sign Up
        if st.button("Create Account"):
            created = create_user(username, password)
            if created:
                st.success("Account created. Please login.")
            else:
                st.error("Username already exists")

    st.stop()  # ⛔ NOTHING below this runs without login

with st.sidebar:
    st.markdown("### 👤 Account")
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.stage = "dashboard"
        st.rerun()



# -------------------------------------------------
# HOME
# -------------------------------------------------
if st.session_state.nav == "Home" and st.session_state.stage is None:
    st.title("🚀 Autonomous Learning Agent")

    st.markdown(
        "<h3 style='text-align:center;'>Learn → Test → Explain → Master</h3>",
        unsafe_allow_html=True
    )

    st.markdown("---")

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
# OVERALL PERFORMANCE
# -------------------------------------------------
elif st.session_state.nav == "Overall Performance":
    st.title("📊 Overall Performance")

    stats = fetch_overall_stats(USER_ID)

    if not stats:
        st.info("No checkpoints attempted yet.")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Checkpoints Attempted", stats["attempted"])
        col2.metric(
            "Total Score",
            f"{stats['total_score']} / {stats['max_score']}"
        )
        col3.metric(
            "Average",
            f"{stats['avg_percentage']:.2f}%"
        )

# -------------------------------------------------
# CHECKPOINT HISTORY
# -------------------------------------------------
elif st.session_state.nav == "Checkpoint History":
    st.title("📌 Checkpoint History")

    history = fetch_checkpoint_history(USER_ID)

    if not history:
        st.info("No checkpoint attempts yet.")
    else:
        for h in history:
            status_icon = "✅" if h["passed"] else "❌"
            status_text = "Passed" if h["passed"] else "Failed"

            st.markdown(f"""
            <div class="history-card">
                <div class="history-title">
                    {h['checkpoint']}
                </div>

                    {status_icon} {status_text} — {h['score']} / {h['total']} ({h['percentage']:.2f}%)

                    {h['timestamp']}
                
            </div>
            """, unsafe_allow_html=True)


# -------------------------------------------------
# LOGIN (PLACEHOLDER)
# -------------------------------------------------
elif st.session_state.nav == "Login":
    st.title("🔐 Login")

    st.info("Single-user mode enabled (USER_ID = 1).")
    st.write("Multi-user auth can be added later.")

# =================================================
# LEARNING PIPELINE (INDEPENDENT OF NAV)
# =================================================

# -------------------------------------------------
# TEACH
# -------------------------------------------------
if st.session_state.stage == "teach":
    checkpoint = checkpoints[st.session_state.checkpoint_index]
    st.title(checkpoint["title"])

    context = teach({"checkpoint": checkpoint})["context"]
    st.session_state.context = context

    st.write(context)

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
        st.markdown(f"**Q{i+1}. {q['question']}**")

        ans = st.radio(
            "",
            options=list(q["options"].keys()),
            format_func=lambda x: f"{x}. {q['options'][x]}",
            key=f"q_{i}"
        )
        user_answers.append(ans)

    if st.button("✅ Submit"):
        result = evaluate_answers(
            st.session_state.questions,
            user_answers,
            st.session_state.context
        )

        percentage = (result["score"] / result["total"]) * 100
        relevance = result["score"] / result["total"]

        save_checkpoint_performance(
            USER_ID,
            st.session_state.checkpoint_index,
            checkpoints[st.session_state.checkpoint_index]["title"],
            result["score"],
            result["total"],
            percentage,
            result["passed"],
            relevance
        )

        st.session_state.result = result
        st.session_state.user_answers = user_answers
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
        <div class="feynman-card">
            <div class="feynman-question">
                ❓ {e['question']}
            </div>

            ❌ Your Answer: {e['user_answer']}    
            ✅ Correct Answer: {e['correct_answer']}
            
            {e['explanation']}
            
        
        """, unsafe_allow_html=True)

    if st.button("🔁 Retry Quiz"):
        st.session_state.stage = "quiz"
        st.rerun()








# -------------------------------------------------
# CHECKPOINT COMPLETED
# -------------------------------------------------
elif st.session_state.stage == "next":
    r = st.session_state.result
    percentage = (r["score"] / r["total"]) * 100

    # 🎉 Celebration
    st.balloons()

    st.success(f"Checkpoint completed — {percentage:.2f}%")

    if st.button("➡ Continue"):
        st.session_state.checkpoint_index += 1
        st.session_state.stage = "teach"
        st.rerun()

    if st.button("🏠 Dashboard"):
        st.session_state.stage = None
        st.rerun()




