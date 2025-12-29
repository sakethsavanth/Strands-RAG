import re

def extract_sections(page_text: str):
    lines = page_text.split("\n")
    sections = []
    current = {"heading": "General", "content": []}

    for line in lines:
        if re.match(r"^[A-Z][A-Za-z\s]{5,}$", line):
            sections.append(current)
            current = {"heading": line.strip(), "content": []}
        else:
            current["content"].append(line)

    sections.append(current)
    return sections
