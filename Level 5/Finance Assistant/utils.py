import re

def extract_final_result(text: str) -> str:
    """
    Robustly extract the last 'Result ---' block (if present).
    Falls back to the full text.
    """
    if not isinstance(text, str):
        return str(text)

    marker = "Result ---"
    last = text.rfind(marker)
    if last == -1:
        # Try a subtask marker
        m = list(re.finditer(r"---\s*Subtask.*?Result\s*---\s*\n", text, flags=re.IGNORECASE | re.DOTALL))
        if m:
            last = m[-1].end()
        else:
            return text.strip()
    else:
        # Move to the end of the line following 'Result ---'
        nl = text.find("\n", last + len(marker))
        last = nl + 1 if nl != -1 else last + len(marker)

    return text[last:].strip()


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)