
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
    fetch_overall_stats,
    
)


from streamlit_option_menu import option_menu




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

/* ---------------- GLOBAL ---------------- */
.stApp {
    background-color: #0E1117;
    color: #E6EDF3;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headings */
h1, h2, h3 {
    color: #00ADB5;
    font-weight: 600;
}

/* ---------------- BUTTONS ---------------- */
.stButton>button {
    background: #00ADB5;
    color: white;
    border-radius: 10px;
    height: 2.8em;
    border: none;
    font-weight: 500;
    transition: 0.2s ease;
}

.stButton>button:hover {
    background: #00cfd5;
    transform: translateY(-1px);
}

/* ---------------- INPUTS ---------------- */
.stTextInput>div>div>input,
.stTextArea textarea {
    background-color: #1E1E1E;
    color: white;
    border-radius: 8px;
}

/* ---------------- GENERIC CARD ---------------- */
.card {
    background: #161B22;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,0.06);
    transition: 0.2s ease;
}

.card:hover {
    transform: translateY(-3px);
}

/* ---------------- HISTORY ---------------- */
.history-card {
    background: #161B22;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.06);
}

.history-title {
    font-size: 1rem;
    font-weight: 600;
}

.history-status {
    font-size: 0.9rem;
    margin-top: 4px;
}

.history-meta {
    font-size: 0.75rem;
    opacity: 0.6;
    margin-top: 6px;
}

/* ---------------- FEYNMAN ---------------- */
.feynman-card {
    background: #161B22;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.06);
}

.feynman-question {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 10px;
}

/* Answer states */
.wrong {
    color: #ff6b6b;
    font-weight: 500;
}

.correct {
    color: #51cf66;
    font-weight: 500;
}

/* ---------------- ANIMATION ---------------- */
.main {
    animation: fadeIn 0.4s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px);}
    to { opacity: 1; transform: translateY(0);}
}

/* ---------------- SIDEBAR ---------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117, #111827);
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




USER_ID = st.session_state.user_id


if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"  # or signup


# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
with st.sidebar:
    selected = option_menu(
        menu_title="🚀 Autonomous Agent",
        options=["Home", "Dashboard", "Analytics", "Checkpoint History"],
        icons=[
            "house",          # Home
            "speedometer2",   # Dashboard (best fit)
            "bar-chart",      # Analytics
            "clock-history"   # History
        ],
        default_index=0,
    )
   

# Reset stage when leaving Home
if selected != "Home":
    st.session_state.stage = None

st.session_state.nav = selected

st.sidebar.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117, #111827);
}
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# HOME
# -------------------------------------------------
# -------------------------------------------------
# HOME
# -------------------------------------------------
if st.session_state.nav == "Home" and st.session_state.stage is None:


    # ---- HERO SECTION ----
    st.markdown("""
    <div style="
        text-align:center;
        padding: 40px 20px;
        border-radius: 16px;
        background: linear-gradient(145deg, #111827, #1f2937);
        border: 1px solid rgba(255,255,255,0.08);
    ">
        <h1 style="margin-bottom:10px;">🚀 Autonomous Learning Agent</h1>
        <p style="opacity:0.8; font-size:16px;">
            Learn smarter with AI-driven checkpoints, quizzes, and feedback
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>📘 Learn</h3>
            <p>Understand concepts with structured content</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>🧠 Test</h3>
            <p>Evaluate your knowledge with quizzes</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>📊 Improve</h3>
            <p>Get feedback and fix weak areas</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    

    # ---- CHECKPOINT SELECTION ----
    st.markdown("""
    <h3 style='text-align:center;'>📚 Choose Your Learning Path</h3>
    """, unsafe_allow_html=True)


    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        selected = st.selectbox(
            "",
            options=list(range(TOTAL_CHECKPOINTS)),
            format_func=lambda i: checkpoints[i]["title"]
        )


    colA, colB, colC = st.columns([1,2,1])

    with colB:
        if st.button("▶ Start Learning", use_container_width=True):
            st.session_state.checkpoint_index = selected
            st.session_state.stage = "teach"
            st.rerun()

        
# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
elif st.session_state.nav == "Dashboard":
    st.title("📊 Dashboard")

    stats = fetch_overall_stats(USER_ID)

    if not stats:
        st.info("No data available yet.")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("📘 Attempted", stats["attempted"])
        col2.metric("🎯 Avg Score", f"{stats['avg_percentage']:.1f}%")
        col3.metric("🏆 Best Score", f"{stats['total_score']}/{stats['max_score']}")

        st.markdown("### 📈 Progress")

        progress = stats["attempted"] / TOTAL_CHECKPOINTS
        progress = max(0.0, min(progress, 1.0))

        st.progress(progress)


# -------------------------------------------------
# ANALYTICS
# -------------------------------------------------
elif st.session_state.nav == "Analytics":
    st.title("📈 Analytics")

    history = fetch_checkpoint_history(USER_ID)

    if not history:
        st.info("No data to analyze yet.")
    else:
        scores = [h["percentage"] for h in history]

        st.markdown("### 📊 Score Trend")
        st.line_chart(scores)

        st.markdown("### 📚 Checkpoint Performance")
        for h in history:
            st.write(h["checkpoint"])
            st.progress(h["percentage"] / 100)


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
            percentage = int(h["percentage"])

            with st.container():
                st.markdown(f"### 📘 {h['checkpoint']}")

                col1, col2 = st.columns([4,1])

                with col1:
                    st.progress(percentage / 100)
                    st.caption(f"🎯 {h['score']} / {h['total']}")

                with col2:
                    if h["passed"]:
                        st.success("Passed")
                    else:
                        st.error("Failed")

                st.caption(f"🕒 {h['timestamp']}")
                st.divider()


# =================================================
# LEARNING PIPELINE
# =================================================

if st.session_state.nav == "Home":

    # ---------------- TEACH ----------------
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

    # ---------------- QUIZ ----------------
    elif st.session_state.stage == "quiz":
        st.title("🧠 Knowledge Check")

        questions = st.session_state.questions
        user_answers = []

        for i, q in enumerate(questions):
            with st.container():
                st.markdown(f"### Q{i+1}. {q['question']}")

                ans = st.radio(
                    "",
                    options=list(q["options"].keys()),
                    format_func=lambda x: f"{x}. {q['options'][x]}",
                    key=f"q_{i}"
                )
                user_answers.append(ans)

                st.divider()

        if st.button("🚀 Submit Quiz"):
            result = evaluate_answers(
                questions,
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

    # ---------------- FEYNMAN ----------------
    elif st.session_state.stage == "feynman":
        st.title("🧠 Let’s Fix the Gaps")

        explanations = feynman_explain(
            st.session_state.questions,
            st.session_state.user_answers
        )

        for e in explanations:
            with st.container():
                st.markdown(f"### ❓ {e['question']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.error(f"Your Answer: {e['user_answer']}")

                with col2:
                    st.success(f"Correct Answer: {e['correct_answer']}")

                st.info(e["explanation"])
                st.divider()

        if st.button("🔁 Retry Quiz"):
            st.session_state.stage = "quiz"
            st.rerun()

    # ---------------- RESULT ----------------
    elif st.session_state.stage == "next":
        r = st.session_state.result
        score = r["score"]
        total = r["total"]
        percentage = (score / total) * 100

        st.balloons()
        st.title("📊 Quiz Result")

        col1, col2, col3 = st.columns(3)

        col1.metric("Score", f"{score}/{total}")
        col2.metric("Percentage", f"{percentage:.1f}%")
        col3.metric("Result", "Passed" if r["passed"] else "Failed")

        if percentage >= 80:
            st.success("Excellent work.")
        elif percentage >= 50:
            st.warning("Needs improvement.")
        else:
            st.error("Weak performance.")

        colA, colB, colC = st.columns(3)

        with colA:
            if st.button("🔁 Retry"):
                st.session_state.stage = "quiz"
                st.rerun()

        with colB:
            if st.button("📘 Review Mistakes"):
                st.session_state.stage = "feynman"
                st.rerun()

        with colC:
            if st.button("➡ Continue"):
                st.session_state.checkpoint_index += 1
                st.session_state.stage = "teach"
                st.rerun()