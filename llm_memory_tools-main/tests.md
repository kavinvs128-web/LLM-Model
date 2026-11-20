# Test results: StudySprint Assistant

All test scenarios were evaluated against the core requirements: Conversational Memory, Custom Tools, No Tool, Scope Enforcement, and Error/Tricky input handling.

| # | Scenario | What I typed | Expected | What happened (short) | Pass? |
|---|---|---|---|---|---|
| 1 | Memory | **Turn 1:** *"My final Calculus exam is scheduled for 2026-12-18 and I have Physics on 2026-12-22."*<br>**Turn 2:** *"When is my Calculus exam again, and what other exam did I mention?"* | Remembers Calculus on 2026-12-18 and Physics on 2026-12-22 from prior messages | Correctly recalled both exam dates and subjects from conversation history without re-prompting | Yes |
| 2 | Tool 1 (`days_until`) | *"How many days are left until my exam on 2026-12-15?"* | Invokes `days_until` with `target_date='2026-12-15'` and reports exact days | Invoked `days_until`, tool returned 25 days remaining relative to today, displayed in Tools used expander | Yes |
| 3 | Tool 2 (`split_study_hours`) | *"I have 12 hours available this weekend to study Algebra, Chemistry, and World History. How should I split my time?"* | Invokes `split_study_hours` with `total_hours=12` and subjects, providing balanced breakdown | Invoked `split_study_hours` (4.0 hrs/subject), displayed subject breakdown in Tools used expander | Yes |
| 4 | No tool needed | *"What are some effective revision techniques for preparing for high-stakes exams?"* | Answers directly with study strategies without triggering any tool calls | Answered with active recall and spaced repetition tips; Tools used box did not appear | Yes |
| 5 | Out of scope | *"Can you recommend the top 3 tech stocks to invest in for maximum returns this year?"* | Politely declines as financial advice is outside study planning scope | Stated it is dedicated exclusively to study/exam planning and declined financial advice | Yes |
| 6 | Tricky (Bad Tool Input) | *"How many days until my test on 'next Tuesday please'?"* | Tool fails gracefully with format instructions; assistant informs user without crashing | Tool caught invalid format, returned guidance to use `YYYY-MM-DD`, assistant politely guided user | Yes |

---

## Detailed Observations

1. **Memory Persistence:** Handled cleanly through `st.session_state.history` storing LangChain message objects across turns up to `MAX_HISTORY = 10`.
2. **Tool Routing:** Clear, single-sentence docstrings in `tools.py` allowed Gemini to accurately select between `days_until`, `split_study_hours`, `reading_time`, and general calculation.
3. **Graceful Degradation:** When given malformed input (`"next Tuesday please"`), `tools.py` returned a structured error message (`Invalid date format...`), which the LLM synthesized into user-friendly guidance.
