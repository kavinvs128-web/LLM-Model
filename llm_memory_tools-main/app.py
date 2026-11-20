"""StudySprint - Personal Study Planner & Exam Prep Assistant.

Built with Streamlit and LangChain.
Visitors bring their own Gemini API key. Keys are held only in session state
and are never logged, stored, or transmitted anywhere else.
"""
import streamlit as st

import assistant_core

st.set_page_config(
    page_title="StudySprint - AI Study Planner",
    page_icon="📚",
    layout="centered",
)

st.title("📚 StudySprint Assistant")
st.caption("Your honest study planning assistant. Bring your own Gemini API key to start.")

# --- SIDEBAR: Configuration & Key Input ---
with st.sidebar:
    st.header("🔑 Authentication")
    api_key = st.text_input(
        "Your Gemini API Key",
        type="password",
        help="Get a free API key at https://aistudio.google.com.",
        placeholder="AIzaSy...",
    )
    st.markdown(
        "[Get a free Gemini API Key](https://aistudio.google.com)  \n"
        "🔒 *Your key stays in your browser memory and is never saved.*"
    )

    st.divider()

    st.header("🛠️ Available Tools")
    st.markdown(
        """
        - **days_until**: Days remaining until an exam/deadline
        - **split_study_hours**: Allocate study hours across subjects
        - **reading_time**: Estimate reading time from text
        - **today**: Current date lookup
        - **calculator**: Mathematical expressions
        """
    )

    st.divider()

    st.header("💡 Try an Example")
    example_prompts = [
        "My Biology exam is on 2026-12-15. How many days do I have left?",
        "I have 15 hours to study Math, Physics, and Chemistry. How should I split it?",
        "When is my Biology exam again? (Memory Test)",
        "Can you recommend the best stock to buy right now? (Out of Scope)",
    ]
    for prompt_text in example_prompts:
        if st.button(prompt_text, key=f"btn_{hash(prompt_text)}"):
            st.session_state["preset_input"] = prompt_text

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.pop("chat", None)
        st.session_state.pop("history", None)
        st.session_state.pop("preset_input", None)
        st.rerun()

    st.caption("⚠️ Disclaimer: StudySprint is an educational planning tool, not an accredited academic advisor.")

# --- API KEY GATEWAY ---
if not api_key:
    st.info("👈 Please paste your free Google Gemini API key in the sidebar to begin chatting.")
    st.markdown(
        """
        ### What StudySprint does:
        1. **Countdown to exams**: Computes exact days remaining until your deadlines.
        2. **Revision allocation**: Divides your available study hours evenly across subjects.
        3. **Reading time estimates**: Calculates how long notes or chapters take to read.
        4. **Conversational memory**: Remembers your subjects, deadlines, and study preferences.
        5. **Honest boundaries**: Politely declines questions unrelated to study planning.
        """
    )
    st.stop()

# --- SESSION STATE INITIALIZATION ---
if "chat" not in st.session_state:
    st.session_state.chat = []  # Display list of (role, text, tools_used)
if "history" not in st.session_state:
    st.session_state.history = []  # LangChain message objects

# --- RENDER CHAT HISTORY ---
for role, text, used in st.session_state.chat:
    with st.chat_message(role):
        st.write(text)
        if used:
            with st.expander("🛠️ Tools used"):
                for u in used:
                    st.markdown(f"**`{u['tool']}`** with args: `{u['args']}`")
                    st.caption(f"Result: {u['result']}")

# --- HANDLE PRESET INPUT OR CHAT INPUT ---
preset = st.session_state.pop("preset_input", None)
question = st.chat_input("Ask StudySprint about your study plan or exams...") or preset

if question:
    st.session_state.chat.append(("user", question, None))
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and planning..."):
            try:
                llm = assistant_core.make_llm(api_key)
                answer, used, st.session_state.history = assistant_core.run_turn(
                    llm, st.session_state.history, question
                )
            except Exception as e:
                answer = f"Something went wrong ({type(e).__name__}: {e}). Please check your API key and try again."
                used = []

            st.write(answer)
            if used:
                with st.expander("🛠️ Tools used"):
                    for u in used:
                        st.markdown(f"**`{u['tool']}`** with args: `{u['args']}`")
                        st.caption(f"Result: {u['result']}")

    st.session_state.chat.append(("assistant", answer, used))
    st.rerun()
