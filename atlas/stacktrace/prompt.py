def build_explainer_prompt(stacktrace: str, frame: dict, code_context: dict) -> str:
    code_snippet = "\n".join(
        f"{line['line_no']:>4}: {line['source']}" for line in code_context["lines"]
    )

    return f"""
You're a senior software engineer helping to diagnose Java stacktraces.

Below is a Java exception stacktrace, along with the relevant source code from the application. Please explain what most likely caused the exception in plain language. If possible, also suggest how a developer should begin debugging it.

---

Stacktrace:
{stacktrace.strip()}

Failing Frame:
- Class: {frame['class']}
- Method: {frame['method']}
- File: {frame['file']}
- Line: {frame['line']}

Code Around Line {frame['line']}:
{code_snippet}

---

Explain:
1. What is most likely happening at this line?
2. Why might it cause an error?
3. What should the developer check or do next?
""".strip()