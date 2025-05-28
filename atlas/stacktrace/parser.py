import re

USER_PACKAGE_PREFIXES = [
    "com.primerevenue",  # <-- You can extend this list
]

def parse_stacktrace(trace_text):
    frame_pattern = re.compile(
        r'\s*at (?P<class>[\w.$]+)\.(?P<method>\w+)\((?P<file>[\w.$]+):(?P<line>\d+)\)'
    )

    parsed_frames = []
    for match in frame_pattern.finditer(trace_text):
        class_name = match.group("class")
        parsed_frames.append({
            "class": class_name,
            "method": match.group("method"),
            "file": match.group("file"),
            "line": int(match.group("line")),
            "is_user_code": any(class_name.startswith(pkg) for pkg in USER_PACKAGE_PREFIXES)
        })

    return parsed_frames