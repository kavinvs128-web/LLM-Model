"""Study Planner assistant tools.

A tool is a normal Python function with a clear docstring and typed inputs.
The model reads the docstring to decide when to use it.
Includes sample general tools plus custom study-planning tools.
"""
import ast
import operator
from datetime import date, datetime

from langchain_core.tools import tool

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("that power is too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / ** % are allowed")


@tool
def calculator(expression: str) -> str:
    """Calculate a maths expression such as '12 * (3 + 4)'. Use it for any arithmetic."""
    try:
        return str(_eval(ast.parse(expression.strip(), mode="eval").body))
    except Exception as e:
        return f"Could not calculate: {e}"


@tool
def today() -> str:
    """Return today's date in YYYY-MM-DD format. Use it when the answer depends on the current date."""
    return date.today().isoformat()


# ---- CUSTOM STUDY PLANNER TOOLS ----

@tool
def days_until(target_date: str) -> str:
    """Calculate how many days remain from today until a target date formatted as YYYY-MM-DD. Use it when the user asks how much time or how many days are left before an exam or deadline."""
    clean_date = target_date.strip().strip("'\"")
    try:
        parsed_date = datetime.strptime(clean_date, "%Y-%m-%d").date()
    except ValueError:
        return f"Invalid date format '{clean_date}'. Please provide the date in YYYY-MM-DD format (for example: '2026-12-15')."

    today_date = date.today()
    delta_days = (parsed_date - today_date).days

    if delta_days > 0:
        return f"There are {delta_days} day(s) remaining until {clean_date} (from today, {today_date.isoformat()})."
    elif delta_days == 0:
        return f"The target date {clean_date} is today ({today_date.isoformat()})!"
    else:
        return f"The target date {clean_date} has already passed ({abs(delta_days)} day(s) ago relative to today {today_date.isoformat()})."


@tool
def split_study_hours(total_hours: float, subjects: str) -> str:
    """Split a total number of study hours evenly across a comma-separated list of subjects. Use it when the user wants to divide study time among specific subjects."""
    if total_hours <= 0:
        return f"Total study hours must be greater than 0 (received {total_hours}). Please provide a positive number of hours."

    # Parse subjects list
    subject_list = [s.strip() for s in subjects.replace(";", ",").split(",") if s.strip()]
    if not subject_list:
        return "Please provide at least one subject separated by commas (for example: 'Math, Physics, History')."

    num_subjects = len(subject_list)
    hours_per_subject = round(total_hours / num_subjects, 2)
    minutes_per_subject = round((total_hours / num_subjects) * 60)

    breakdown = "\n".join(
        f"- {subject}: {hours_per_subject} hr(s) (~{minutes_per_subject} mins)"
        for subject in subject_list
    )
    return (
        f"Distributed {total_hours} total hour(s) across {num_subjects} subject(s):\n"
        f"{breakdown}\n"
        f"Average time per subject: {hours_per_subject} hours."
    )


@tool
def reading_time(text: str) -> str:
    """Estimate how many minutes it takes to read a study text or notes snippet. Use it when the user provides study text or notes and asks how long it will take to read."""
    stripped = text.strip()
    if not stripped:
        return "Please provide a non-empty text snippet to estimate reading time."
    words = len(stripped.split())
    minutes = max(1, round(words / 200))
    return f"Text contains {words} words. Estimated reading time is approximately {minutes} minute(s) at an average speed of 200 words per minute."


TOOLS = [calculator, today, days_until, split_study_hours, reading_time]
