# StudySprint - AI Study Planner & Exam Prep Assistant

**Live app:** [https://studysprint-assistant.streamlit.app](https://studysprint-assistant.streamlit.app) *(Deploy your fork to Streamlit Cloud; paste your own free Gemini API key in the sidebar)*

## Topic and user
StudySprint is designed for high school and university students preparing for exams, managing tight revision schedules, and organizing study deadlines. It helps learners calculate exact countdowns to exam dates, evenly balance study hours across multiple subjects, and estimate reading times for study material.

## My tools
| Tool | What it does | Example question that uses it |
|---|---|---|
| `days_until` | Computes the exact number of days remaining from today until a target deadline formatted as `YYYY-MM-DD`. | *"How many days do I have left until my Biology exam on 2026-12-15?"* |
| `split_study_hours` | Evenly distributes a total number of study hours across a comma-separated list of subjects, providing hour and minute breakdowns. | *"I have 12 hours available this weekend to study Algebra, Chemistry, and History. How should I split my time?"* |
| `reading_time` | Estimates the reading duration in minutes based on word count at an average pace of 200 words per minute. | *"How long will it take me to read through these 1,500 words of lecture summary notes?"* |
| `today` | Returns today's current date in `YYYY-MM-DD` format so the assistant never guesses the current date. | *"What is today's date?"* |
| `calculator` | Safely evaluates arithmetic expressions using Python AST. | *"What is 15 * 4.5 minus 10?"* |

## What it will not do
- **Off-topic queries:** StudySprint strictly declines questions outside study planning, such as financial/stock market recommendations, medical diagnostics, legal advice, general coding tasks, or entertainment trivia.
- **Hallucinated dates or calculations:** It refuses to guess dates, intervals, or arithmetic. It relies strictly on its local Python tools and politely guides the user if given malformed input.

## Test results
**6 of 6 passed (100%).**
All 6 test scenarios (Conversational Memory, Tool 1 `days_until`, Tool 2 `split_study_hours`, Direct response without tools, Scope boundary refusal, and Graceful handling of invalid tool inputs) passed cleanly. See [`tests.md`](./tests.md) for full transcripts and evaluation evidence.

## My answers
### 1. In my own words: what happens between a user's question and the answer, when a tool is used?
When a user submits a question, `run_turn` constructs a message sequence consisting of the system prompt, the recent conversation history stored in session state, and the new user message. This sequence is sent to Gemini, which has been configured with our tool signatures via `llm.bind_tools(TOOLS)`. Recognizing that the answer requires exact computation or live dates, the model returns an `AIMessage` with a `tool_calls` payload specifying the tool function name and typed arguments instead of plain text. 

The application loop inspects this payload, looks up the corresponding Python function in our local tool dictionary, executes the function safely in local Python, and packages the result into a `ToolMessage` linked by the unique `tool_call_id`. This `ToolMessage` is appended to the message list and sent back to Gemini in the next loop iteration (`MAX_STEPS = 4`). Gemini interprets the tool's exact output and formulates a helpful, natural-language response incorporating the verified facts.

### 2. How does my assistant remember the conversation, and what is its limit?
StudySprint maintains conversational memory by appending every user input (`HumanMessage`) and assistant response (`AIMessage`) to a list in Streamlit's `st.session_state.history`. On each turn, the most recent messages are injected directly into the LLM context between the system prompt and the current prompt, enabling the assistant to recall facts stated in earlier turns (such as exam subjects or deadlines).

The memory limit is governed by `MAX_HISTORY = 10` messages (representing the last 5 complete conversational turns). This sliding window keeps the prompt compact, prevents latency spikes and token waste, and avoids hitting model context limits. Furthermore, clicking the **"Clear chat"** button in the sidebar completely removes `history` from session state, immediately resetting the assistant's memory to zero.

---

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/studysprint-assistant.git
   cd studysprint-assistant
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   streamlit run app.py
   ```

5. **Bring Your Own Key:**
   Enter your free Gemini API key from [Google AI Studio](https://aistudio.google.com) into the sidebar input field.
