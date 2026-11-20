"""Core logic for the Study Planner assistant.

Manages conversational memory, LLM tool-calling loop, and system prompt limits.
"""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import TOOLS

CHAT_MODEL = "gemini-3.5-flash-lite"
MAX_HISTORY = 10  # number of past messages retained in conversational memory
MAX_STEPS = 4  # max tool-calling loop steps per question

SYSTEM_PROMPT = """You are StudySprint, a focused, honest Study Planner and Exam Preparation assistant.
Your job is strictly to help students plan study sessions, split revision hours, estimate reading time, and calculate days until exam deadlines.

Core Rules:
1. Scope Limit: ONLY answer questions related to studying, exam schedules, revision plans, study time allocation, and reading estimations.
2. Polite Refusal: If a question is outside study planning (e.g. general software coding, financial investing, medical diagnosis, cooking, sports, legal matters), politely decline and state your scope. Example refusal: "I am dedicated exclusively to study and exam planning. I cannot assist with [topic], but I would be glad to help organize your study schedule or calculate revision timelines!"
3. Tool Usage: Always use your tools for exact calculations, current date lookups, countdowns to deadlines, and study hour allocations. Never guess numbers or dates that a tool can calculate for you.
4. Tool Failures: If a tool reports an invalid input (e.g., malformed date or zero study hours), explain the issue clearly and politely guide the user on the required format.
5. Conversational Memory: Remember facts the user shared earlier (e.g. their exam dates, subjects, available hours) and refer back to them when planning subsequent study sessions.
6. Honesty: If you are unsure or lack sufficient information, say so clearly instead of guessing."""


def make_llm(api_key: str):
    """Instantiate the Gemini chat model with the visitor's API key."""
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        temperature=0.2,
        google_api_key=api_key,
    )


def text_of(content):
    """Extract plain string content from Gemini responses that may return part objects."""
    if isinstance(content, str):
        return content
    return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)


def run_turn(llm, history, question, system_prompt=SYSTEM_PROMPT):
    """Answer one user question using the tool loop.

    Returns:
        tuple: (answer_text, tools_used_list, updated_history)
    """
    by_name = {t.name: t for t in TOOLS}
    llm_with_tools = llm.bind_tools(TOOLS)
    messages = [SystemMessage(content=system_prompt)] + history[-MAX_HISTORY:] + [HumanMessage(content=question)]
    used = []
    answer = ""

    for _ in range(MAX_STEPS):
        ai = llm_with_tools.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            answer = text_of(ai.content)
            break

        for call in ai.tool_calls:
            tool = by_name.get(call["name"])
            if tool is None:
                result = ToolMessage(
                    content="No such tool available.",
                    tool_call_id=call["id"],
                    name=call["name"],
                )
            else:
                try:
                    result = tool.invoke(call)
                except Exception as e:
                    result = ToolMessage(
                        content=f"Tool error: {e}",
                        tool_call_id=call["id"],
                        name=call["name"],
                    )
            used.append({"tool": call["name"], "args": call["args"], "result": str(result.content)})
            messages.append(result)

    if not answer:
        answer = "I could not complete that request within the allowed steps. Please try rephrasing your question."

    new_history = (history + [HumanMessage(content=question), AIMessage(content=answer)])[-MAX_HISTORY:]
    return answer, used, new_history
