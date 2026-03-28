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
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests



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

/* App background */
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}

/* Remove default padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headings */
h1, h2, h3 {
    color: #00ADB5;
    font-weight: 600;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #00ADB5, #007B83);
    color: white;
    border-radius: 12px;
    height: 3em;
    border: none;
    font-weight: 500;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
    background: #00cfd5;
}

/* Inputs */
.stTextInput>div>div>input,
.stTextArea textarea {
    background-color: #1E1E1E;
    color: white;
    border-radius: 10px;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.main {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px);}
    to { opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.card {
    transition: all 0.25s ease;
}
.card:hover {
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 12px 30px rgba(0,0,0,0.6);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.feynman-card {
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 22px;
    border-radius: 16px;
    margin-bottom: 25px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.35);
    transition: all 0.25s ease;
}

.feynman-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.6);
}

.answer-box {
    padding: 10px;
    border-radius: 10px;
    font-weight: 500;
}

.wrong {
    background: rgba(255, 107, 107, 0.2);
    color: #ff6b6b;
}

.correct {
    background: rgba(81, 207, 102, 0.2);
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

    # ---------- HEADER ----------
    st.markdown("""
    <div style="
        max-width: 800px;
        margin: auto;
        padding: 30px;
        border-radius: 15px;
        background: linear-gradient(145deg, #111827, #1f2937);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        text-align: center;
    ">
        <h1 style="margin-bottom:10px;">🚀 Autonomous Learning Agent</h1>
        <p style="opacity:0.8; font-size:16px;">
            Learn → Test → Explain → Master
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    

    # ---------- SELECTBOX (CENTERED) ----------
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        selected = st.selectbox(
            "📚 Choose a checkpoint",
            options=list(range(TOTAL_CHECKPOINTS)),
            format_func=lambda i: checkpoints[i]["title"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- BUTTON (PERFECT CENTER) ----------
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
        # ---- TOP METRICS ----
        col1, col2, col3 = st.columns(3)

        col1.metric("📘 Attempted", stats["attempted"])
        col2.metric("🎯 Avg Score", f"{stats['avg_percentage']:.1f}%")
        col3.metric("🏆 Best Score", f"{stats['total_score']}/{stats['max_score']}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- PROGRESS ----
        st.markdown("### 📈 Progress")
        progress = stats["attempted"] / TOTAL_CHECKPOINTS

        # Safety fix (important)
        progress = max(0.0, min(progress, 1.0))

        progress_bar = st.progress(0)

        for i in range(int(progress * 100)):
            progress_bar.progress((i + 1) / 100)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- SUMMARY ----
        st.markdown("### 🧠 Summary")

        if stats["avg_percentage"] >= 75:
            st.success("Strong performance. Keep pushing forward.")
        elif stats["avg_percentage"] >= 50:
            st.warning("Decent progress, but improvement needed.")
        else:
            st.error("Weak performance. Focus on fundamentals.")




# -------------------------------------------------
# OVERALL PERFORMANCE
# -------------------------------------------------

elif st.session_state.nav == "Analytics":
    st.title("📈 Analytics")

    history = fetch_checkpoint_history(USER_ID)

    if not history:
        st.info("No data to analyze yet.")
    else:
        scores = [h["percentage"] for h in history]
        checkpoints_names = [h["checkpoint"] for h in history]

        # ---- SCORE TREND ----
        st.markdown("### 📊 Score Trend")
        st.line_chart(scores)

        # ---- CHECKPOINT PERFORMANCE ----
        st.markdown("### 📚 Checkpoint Performance")
        for h in history:
            st.write(f"{h['checkpoint']}")
            st.progress(h["percentage"] / 100)

        # ---- WEAK AREAS ----
        st.markdown("### ❗ Weak Areas")

        weak = [h for h in history if h["percentage"] < 50]

        if weak:
            for w in weak:
                st.error(f"{w['checkpoint']} ({w['percentage']:.1f}%)")
        else:
            st.success("No weak areas detected 🎉")


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
            status = "✅ Passed" if h["passed"] else "❌ Failed"

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


if st.session_state.nav == "Home":

    # ---------------- TEACH ----------------
    if st.session_state.stage == "teach":
        checkpoint = checkpoints[st.session_state.checkpoint_index]
        st.title(checkpoint["title"])

        context = teach({"checkpoint": checkpoint})["context"]
        st.session_state.context = context

        st.write(context)

        if st.button("📝 Start Quiz"):
            with st.spinner("Generating quiz..."):
                st.session_state.questions = generate_mcqs(context)

            st.session_state.stage = "quiz"
            st.rerun()

    # ---------------- QUIZ ----------------
    elif st.session_state.stage == "quiz":
        st.title("🧠 Knowledge Check")

        if "questions" not in st.session_state:
            st.error("No questions found. Go back and start again.")
            st.stop()

        

        questions = st.session_state.questions

        if not questions:
            st.error("Questions list is empty.")
            st.stop()

        total_q = len(questions)
        user_answers = []

        current_progress = sum([1 for i in range(total_q) if f"q_{i}" in st.session_state])
        

        for i, q in enumerate(st.session_state.questions):

            with st.container():

                # Card Title
                st.markdown(f"### Q{i+1}. {q['question']}")

                # Options
                ans = st.radio(
                    "",
                    options=list(q["options"].keys()),
                    format_func=lambda x: f"{x}. {q['options'][x]}",
                    key=f"q_{i}"
                )

                user_answers.append(ans)

                # Bottom spacing + divider
                st.markdown("<br>", unsafe_allow_html=True)
                st.divider()

        col1, col2, col3 = st.columns([1,2,1])

        with col2:
            submit = st.button("🚀 Submit Quiz", use_container_width=True)

        if submit:
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
                st.subheader(e['question'])

                col1, col2 = st.columns(2)

                with col1:
                    st.error(f"Your Answer: {e['user_answer']}")

                with col2:
                    st.success(f"Correct Answer: {e['correct_answer']}")

                st.write(e["explanation"])
                st.divider()

        colA, colB, colC = st.columns([1,2,1])
        with colB:
            if st.button("🔁 Retry Quiz", use_container_width=True):
                st.session_state.stage = "quiz"
                st.rerun()

    # ---------------- RESULT ----------------
    elif st.session_state.stage == "next":

        r = st.session_state.result
        score = r["score"]
        total = r["total"]
        percentage = (score / total) * 100

        # 🎯 Title
        st.title("📊 Quiz Result")

        # 🟢 Score Summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Score", f"{score}/{total}")

        with col2:
            st.metric("Percentage", f"{percentage:.1f}%")

        with col3:
            status = "✅ Passed" if r["passed"] else "❌ Failed"
            st.metric("Result", status)

        st.divider()

        # 🧠 Performance Insight
        if percentage >= 80:
            st.success("Excellent work. You have strong understanding.")
        elif percentage >= 50:
            st.warning("Decent, but there are gaps to improve.")
        else:
            st.error("Weak understanding. You should review concepts.")

        st.divider()

        # 🚀 Actions
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



