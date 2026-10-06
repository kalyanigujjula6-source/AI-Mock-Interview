import os
import io
import json
import re
import time

import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT & PAGE CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AI Mock Interview",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.main {
    background: linear-gradient(135deg, #0f172a, #172554, #312e81);
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero-box {
    padding: 30px;
    border-radius: 24px;
    background: linear-gradient(135deg, #2563eb, #7c3aed, #db2777);
    color: white;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.30);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
}

.hero-subtitle {
    font-size: 18px;
}

.question-box {
    padding: 25px;
    border-radius: 20px;
    background: linear-gradient(135deg, #0284c7, #2563eb);
    color: white;
    margin-top: 20px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
}

.voice-box {
    padding: 22px;
    border-radius: 20px;
    background: linear-gradient(135deg, #047857, #0f766e);
    color: white;
    margin-top: 15px;
    margin-bottom: 20px;
}

.feature-box {
    padding: 20px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    margin-bottom: 20px;
}

.correct-box {
    padding: 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, #065f46, #047857);
    color: white;
    margin-top: 15px;
    margin-bottom: 15px;
}

.better-box {
    padding: 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, #7c2d12, #c2410c);
    color: white;
    margin-top: 15px;
    margin-bottom: 15px;
}

.improvement-box {
    padding: 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, #1e3a8a, #3730a3);
    color: white;
    margin-top: 15px;
    margin-bottom: 15px;
}

.recommendation-box {
    padding: 22px;
    border-radius: 20px;
    background: linear-gradient(135deg, #9a3412, #c2410c);
    color: white;
    margin-top: 25px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GEMINI API CHECK
# ============================================================

if not API_KEY:
    st.error("❌ GEMINI_API_KEY not found in .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)


# ============================================================
# GEMINI MODEL CANDIDATES
# ============================================================

MODEL_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]


# ============================================================
# GEMINI REQUEST FUNCTION
# ============================================================

def ask_gemini(prompt):
    last_error = None

    for model_name in MODEL_CANDIDATES:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

                if response and response.text:
                    return response.text.strip()

            except Exception as error:
                last_error = error
                time.sleep(1)

    raise RuntimeError(
        f"Gemini service is temporarily unavailable. "
        f"Last error: {last_error}"
    )


# ============================================================
# GENERATE INTERVIEW QUESTION
# ============================================================

def generate_question(
    candidate_name,
    role,
    interview_type,
    question_number
):
    prompt = f"""
You are an expert professional interviewer.

Candidate Name:
{candidate_name}

Role:
{role}

Interview Type:
{interview_type}

Question Number:
{question_number}

Generate ONE professional interview question.

Requirements:
- Suitable for the selected role.
- Suitable for the selected interview type.
- Test practical understanding.
- Appropriate difficulty.
- Avoid unnecessarily generic questions.
- Do not include the answer.
- Return ONLY the interview question.
"""

    return ask_gemini(prompt)


# ============================================================
# CHECK IF CANDIDATE DOES NOT KNOW THE ANSWER
# ============================================================

def is_unknown_answer(answer):
    text = answer.lower().strip()

    unknown_patterns = [
        "i don't know",
        "i dont know",
        "i do not know",
        "don't know",
        "dont know",
        "do not know",
        "i have no idea",
        "no idea",
        "not sure",
        "i'm not sure",
        "im not sure",
        "i am not sure",
        "cannot answer",
        "can't answer",
        "cant answer",
        "unable to answer",
        "i don't have an answer",
        "i dont have an answer",
    ]

    return any(
        phrase in text
        for phrase in unknown_patterns
    )


# ============================================================
# EVALUATE ANSWER
# ============================================================

def evaluate_answer(question, answer, role):

    unknown_answer = is_unknown_answer(answer)

    if unknown_answer:
        special_instruction = """
The candidate explicitly indicated that they do not know the answer.

Therefore:
- Treat the answer as incorrect/incomplete.
- Technical score should normally be between 1 and 3.
- Relevance score should normally be between 1 and 3.
- Overall score should normally be between 1 and 3.
- Communication score can be higher if the candidate clearly communicated that they do not know.
- Clearly explain that the candidate should learn this concept.
- Provide the correct answer.
- Provide an excellent interview-quality better answer.
"""
    else:
        special_instruction = """
Evaluate the candidate answer fairly.
If the answer is partially correct, identify the missing points.
If the answer is incorrect, explain the mistake.
If the answer is correct, acknowledge its strengths and provide a more polished interview-quality answer.
"""

    prompt = f"""
You are an expert professional interview evaluator.

Candidate Role:
{role}

Interview Question:
{question}

Candidate Answer:
{answer}

{special_instruction}

Evaluate the candidate on:

1. Technical Score
2. Communication Score
3. Relevance Score
4. Overall Score

Scores must be from 1 to 10.

Also provide:

- Feedback
- Strengths
- Improvement
- Correct Answer
- Better Interview Answer

The "correct_answer" must explain the concept accurately.

The "better_answer" must be a natural answer that a candidate could actually say in a professional interview.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "technical": 0,
    "communication": 0,
    "relevance": 0,
    "overall": 0,
    "feedback": "text",
    "improvement": "text",
    "strengths": "text",
    "correct_answer": "text",
    "better_answer": "text"
}}
"""

    raw_response = ask_gemini(prompt)

    cleaned = raw_response.strip()

    cleaned = re.sub(
        r"```json",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"```",
        "",
        cleaned
    ).strip()

    try:
        evaluation = json.loads(cleaned)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "Gemini returned an invalid evaluation format."
            )

        evaluation = json.loads(match.group(0))

    # Make sure all expected fields exist.
    evaluation.setdefault("technical", 0)
    evaluation.setdefault("communication", 0)
    evaluation.setdefault("relevance", 0)
    evaluation.setdefault("overall", 0)
    evaluation.setdefault(
        "feedback",
        "No feedback available."
    )
    evaluation.setdefault(
        "improvement",
        "No improvement suggestion available."
    )
    evaluation.setdefault(
        "strengths",
        "No strengths information available."
    )
    evaluation.setdefault(
        "correct_answer",
        "Correct answer was not provided."
    )
    evaluation.setdefault(
        "better_answer",
        "Better answer was not provided."
    )

    return evaluation


# ============================================================
# VOICE TO TEXT
# ============================================================

def convert_voice_to_text(audio_bytes):

    recognizer = sr.Recognizer()

    try:

        audio_file = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(
            audio_data
        )

        return text

    except sr.UnknownValueError:

        raise ValueError(
            "I could not understand the audio. "
            "Please speak clearly and try again."
        )

    except sr.RequestError:

        raise ValueError(
            "Speech recognition service is unavailable. "
            "Please check your internet connection."
        )

    except Exception as error:

        raise ValueError(
            f"Voice processing failed: {error}"
        )


# ============================================================
# SESSION STATE
# ============================================================

default_values = {

    "started": False,

    "finished": False,

    "candidate_name": "",

    "role": "",

    "interview_type": "",

    "question_number": 0,

    "question_count": 5,

    "current_question": "",

    "results": [],

    "voice_answer": "",
}


for key, value in default_values.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
<div class="hero-box">

<div class="hero-title">
🎤 AI-Powered Mock Interview
</div>

<div class="hero-subtitle">
Practice • Speak • Get AI Feedback • Improve 🚀
</div>

</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Interview Settings")

    if not st.session_state.started:

        candidate_name = st.text_input(
            "👤 Candidate Name",
            placeholder="Enter your name",
        )

        role = st.selectbox(
            "💼 Interview Role",
            [
                "Python Developer",
                "Data Scientist",
                "Machine Learning Engineer",
                "Web Developer",
                "Software Developer",
                "AI Engineer",
            ],
        )

        interview_type = st.selectbox(
            "🎯 Interview Type",
            [
                "Technical Interview",
                "HR Interview",
                "Mixed Interview",
            ],
        )

        question_count = st.selectbox(
            "🔢 Number of Questions",
            [3, 5, 7, 10],
            index=1,
        )

        start_button = st.button(
            "🚀 Start Interview",
            use_container_width=True,
        )

        if start_button:

            if not candidate_name.strip():

                st.warning(
                    "⚠️ Please enter your name."
                )

            else:

                with st.spinner(
                    "🤖 Gemini is preparing your interview..."
                ):

                    try:

                        first_question = generate_question(
                            candidate_name,
                            role,
                            interview_type,
                            1,
                        )

                        st.session_state.started = True
                        st.session_state.finished = False

                        st.session_state.candidate_name = (
                            candidate_name
                        )

                        st.session_state.role = role

                        st.session_state.interview_type = (
                            interview_type
                        )

                        st.session_state.question_number = 1

                        st.session_state.question_count = (
                            question_count
                        )

                        st.session_state.current_question = (
                            first_question
                        )

                        st.session_state.results = []

                        st.session_state.voice_answer = ""

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "⚠️ Gemini AI is temporarily unavailable."
                        )

                        st.caption(str(error))

    else:

        st.success("🟢 Interview in progress")

        st.write(
            f"👤 **{st.session_state.candidate_name}**"
        )

        st.write(
            f"💼 **{st.session_state.role}**"
        )

        st.write(
            f"🎯 **{st.session_state.interview_type}**"
        )

        total_questions = (
            st.session_state.question_count
        )

        current_number = (
            st.session_state.question_number
        )

        progress_value = min(
            current_number / total_questions,
            1.0
        )

        st.progress(progress_value)

        st.write(
            f"📊 Question {current_number}/{total_questions}"
        )


# ============================================================
# START SCREEN
# ============================================================

if not st.session_state.started:

    st.markdown(
        """
<div class="feature-box">

<h2>🌟 Welcome to your AI Interview Practice Room!</h2>

<p>🤖 AI-generated interview questions</p>

<p>🎤 Voice answers using your microphone</p>

<p>📝 Automatic speech-to-text conversion</p>

<p>🧠 Gemini AI answer evaluation</p>

<p>📊 Technical, Communication & Relevance scores</p>

<p>❌ Wrong answer detection</p>

<p>✅ Correct answer explanation</p>

<p>⭐ Better interview answer generation</p>

<p>💡 Personalized improvement suggestions</p>

<p>🏆 Final interview performance report</p>

</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🎯 Real Interview Questions"
        )

    with col2:

        st.success(
            "🎤 Voice + Text Answers"
        )

    with col3:

        st.warning(
            "📊 AI Performance Report"
        )


# ============================================================
# INTERVIEW SCREEN
# ============================================================

elif (
    st.session_state.started
    and not st.session_state.finished
):

    question_number = (
        st.session_state.question_number
    )

    total_questions = (
        st.session_state.question_count
    )

    st.markdown(
        f"""
<div class="question-box">

<h2>🤔 Question {question_number}</h2>

</div>
""",
        unsafe_allow_html=True,
    )

    st.write(
        st.session_state.current_question
    )

    # --------------------------------------------------------
    # VOICE SECTION
    # --------------------------------------------------------

    st.markdown(
        """
<div class="voice-box">

<h2>🎤 Voice Answer</h2>

<p>
Click the microphone button below and speak your answer.
</p>

</div>
""",
        unsafe_allow_html=True,
    )

    audio_value = st.audio_input(
        "🎙️ Record your answer"
    )

    if audio_value is not None:

        st.audio(
            audio_value,
            format="audio/wav"
        )

        convert_button = st.button(
            "📝 Convert Voice to Text",
            use_container_width=True,
        )

        if convert_button:

            with st.spinner(
                "🎧 Converting your speech to text..."
            ):

                try:

                    converted_text = (
                        convert_voice_to_text(
                            audio_value.getvalue()
                        )
                    )

                    st.session_state.voice_answer = (
                        converted_text
                    )

                    st.success(
                        "✅ Voice converted successfully!"
                    )

                    st.info(
                        f"📝 **Recognized Answer:** "
                        f"{converted_text}"
                    )

                except ValueError as error:

                    st.error(
                        f"❌ {error}"
                    )

    # --------------------------------------------------------
    # TEXT ANSWER
    # --------------------------------------------------------

    st.subheader("💬 Your Answer")

    answer_text = st.text_area(
        "Type your answer OR use the voice answer above.",
        value=st.session_state.voice_answer,
        placeholder=(
            "Your answer will appear here "
            "after voice conversion..."
        ),
        height=220,
    )

    submit_button = st.button(
        "📤 Submit Answer for AI Evaluation",
        use_container_width=True,
    )

    if submit_button:

        final_answer = answer_text.strip()

        if not final_answer:

            st.warning(
                "⚠️ Please type an answer or record a voice answer."
            )

        else:

            with st.spinner(
                "🤖 Gemini is evaluating your answer..."
            ):

                try:

                    evaluation = evaluate_answer(
                        st.session_state.current_question,
                        final_answer,
                        st.session_state.role,
                    )

                    result = {

                        "question":
                            st.session_state.current_question,

                        "answer":
                            final_answer,

                        "evaluation":
                            evaluation,
                    }

                    st.session_state.results.append(
                        result
                    )

                    st.success(
                        "✅ Answer evaluated successfully!"
                    )

                    # ------------------------------------------------
                    # SHOW QUICK FEEDBACK BEFORE NEXT QUESTION
                    # ------------------------------------------------

                    st.subheader(
                        "📊 Quick AI Evaluation"
                    )

                    eval_col1, eval_col2, eval_col3, eval_col4 = (
                        st.columns(4)
                    )

                    with eval_col1:
                        st.metric(
                            "🎯 Technical",
                            f"{evaluation.get('technical', 0)}/10"
                        )

                    with eval_col2:
                        st.metric(
                            "💬 Communication",
                            f"{evaluation.get('communication', 0)}/10"
                        )

                    with eval_col3:
                        st.metric(
                            "📌 Relevance",
                            f"{evaluation.get('relevance', 0)}/10"
                        )

                    with eval_col4:
                        st.metric(
                            "🏆 Overall",
                            f"{evaluation.get('overall', 0)}/10"
                        )

                    st.write("### 📝 AI Feedback")

                    st.write(
                        evaluation.get(
                            "feedback",
                            "No feedback available."
                        )
                    )

                    # Correct Answer
                    st.markdown(
                        """
<div class="correct-box">

<h3>✅ Correct Answer</h3>

</div>
""",
                        unsafe_allow_html=True,
                    )

                    st.write(
                        evaluation.get(
                            "correct_answer",
                            "Correct answer not available."
                        )
                    )

                    # Better Answer
                    st.markdown(
                        """
<div class="better-box">

<h3>⭐ Better Interview Answer</h3>

</div>
""",
                        unsafe_allow_html=True,
                    )

                    st.write(
                        evaluation.get(
                            "better_answer",
                            "Better answer not available."
                        )
                    )

                    # Improvement
                    st.markdown(
                        """
<div class="improvement-box">

<h3>💡 How to Improve</h3>

</div>
""",
                        unsafe_allow_html=True,
                    )

                    st.write(
                        evaluation.get(
                            "improvement",
                            "No improvement suggestion available."
                        )
                    )

                    if question_number < total_questions:

                        with st.spinner(
                            "🤖 Preparing your next question..."
                        ):

                            next_question = (
                                generate_question(
                                    st.session_state.candidate_name,
                                    st.session_state.role,
                                    st.session_state.interview_type,
                                    question_number + 1,
                                )
                            )

                        st.session_state.question_number += 1

                        st.session_state.current_question = (
                            next_question
                        )

                        st.session_state.voice_answer = ""

                        st.rerun()

                    else:

                        st.session_state.finished = True

                        st.rerun()

                except Exception as error:

                    st.error(
                        "⚠️ AI evaluation failed."
                    )

                    st.caption(str(error))


# ============================================================
# FINAL REPORT
# ============================================================

elif st.session_state.finished:

    st.title(
        "🏆 Interview Completed!"
    )

    st.write(
        "Your AI-powered performance report is ready."
    )

    results = st.session_state.results

    technical_scores = []

    communication_scores = []

    relevance_scores = []

    overall_scores = []

    for item in results:

        evaluation = item["evaluation"]

        technical_scores.append(
            int(evaluation.get("technical", 0))
        )

        communication_scores.append(
            int(evaluation.get("communication", 0))
        )

        relevance_scores.append(
            int(evaluation.get("relevance", 0))
        )

        overall_scores.append(
            int(evaluation.get("overall", 0))
        )

    def calculate_average(values):

        if not values:
            return 0

        return round(
            sum(values) / len(values),
            1
        )

    average_technical = calculate_average(
        technical_scores
    )

    average_communication = calculate_average(
        communication_scores
    )

    average_relevance = calculate_average(
        relevance_scores
    )

    average_overall = calculate_average(
        overall_scores
    )

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    st.subheader(
        "📊 Your Performance"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🎯 Technical",
            f"{average_technical}/10"
        )

    with col2:

        st.metric(
            "💬 Communication",
            f"{average_communication}/10"
        )

    with col3:

        st.metric(
            "📌 Relevance",
            f"{average_relevance}/10"
        )

    with col4:

        st.metric(
            "🏆 Overall",
            f"{average_overall}/10"
        )

    st.divider()

    # --------------------------------------------------------
    # OVERALL RECOMMENDATION
    # --------------------------------------------------------

    if average_overall >= 8.5:

        st.success(
            "🌟 Excellent performance! "
            "You are showing strong interview readiness."
        )

    elif average_overall >= 7:

        st.info(
            "👍 Good performance! "
            "With some improvement, you can become interview-ready."
        )

    elif average_overall >= 5:

        st.warning(
            "📚 Fair performance. "
            "More practice will significantly improve your results."
        )

    else:

        st.error(
            "💪 Keep practicing! "
            "Focus on fundamentals and communication."
        )

    # --------------------------------------------------------
    # DETAILED EVALUATION
    # --------------------------------------------------------

    st.subheader(
        "📝 Detailed Question-by-Question Evaluation"
    )

    for index, item in enumerate(
        results,
        start=1
    ):

        evaluation = item["evaluation"]

        score = evaluation.get(
            "overall",
            0
        )

        with st.expander(
            f"Question {index} — Overall Score: {score}/10"
        ):

            st.write(
                "### 🤔 Question"
            )

            st.write(
                item["question"]
            )

            st.write(
                "### 💬 Your Answer"
            )

            st.write(
                item["answer"]
            )

            # -----------------------------------------------
            # SCORES
            # -----------------------------------------------

            st.write(
                "### 📊 Scores"
            )

            score_col1, score_col2, score_col3 = (
                st.columns(3)
            )

            with score_col1:

                st.write(
                    f"🎯 Technical: "
                    f"**{evaluation.get('technical', 0)}/10**"
                )

            with score_col2:

                st.write(
                    f"💬 Communication: "
                    f"**{evaluation.get('communication', 0)}/10**"
                )

            with score_col3:

                st.write(
                    f"📌 Relevance: "
                    f"**{evaluation.get('relevance', 0)}/10**"
                )

            # -----------------------------------------------
            # FEEDBACK
            # -----------------------------------------------

            st.write(
                "### 📝 AI Feedback"
            )

            st.write(
                evaluation.get(
                    "feedback",
                    "No feedback available."
                )
            )

            # -----------------------------------------------
            # STRENGTHS
            # -----------------------------------------------

            st.write(
                "### 💪 Strengths"
            )

            st.write(
                evaluation.get(
                    "strengths",
                    "No strengths information available."
                )
            )

            # -----------------------------------------------
            # IMPROVEMENT
            # -----------------------------------------------

            st.write(
                "### 💡 Improvement"
            )

            st.write(
                evaluation.get(
                    "improvement",
                    "No improvement suggestion available."
                )
            )

            # -----------------------------------------------
            # CORRECT ANSWER
            # -----------------------------------------------

            st.markdown(
                """
<div class="correct-box">

<h3>✅ Correct Answer</h3>

</div>
""",
                unsafe_allow_html=True,
            )

            st.write(
                evaluation.get(
                    "correct_answer",
                    "Correct answer was not provided."
                )
            )

            # -----------------------------------------------
            # BETTER INTERVIEW ANSWER
            # -----------------------------------------------

            st.markdown(
                """
<div class="better-box">

<h3>⭐ Better Interview Answer</h3>

</div>
""",
                unsafe_allow_html=True,
            )

            st.write(
                evaluation.get(
                    "better_answer",
                    "Better answer was not provided."
                )
            )

    # --------------------------------------------------------
    # CAREER RECOMMENDATION
    # --------------------------------------------------------

    st.markdown(
        """
<div class="recommendation-box">

<h2>💡 AI Career Recommendation</h2>

🎯 Practice technical concepts

💬 Improve communication

🧠 Use practical examples

🗣️ Structure answers clearly

🎤 Practice speaking confidently

📚 Review the correct answers after every question

⭐ Practice giving better interview-quality answers

🚀 Continue mock interview practice

</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # NEW INTERVIEW
    # --------------------------------------------------------

    if st.button(
        "🔄 Start New Interview",
        use_container_width=True,
    ):

        for key in default_values:

            if key in st.session_state:

                del st.session_state[key]

        st.rerun()