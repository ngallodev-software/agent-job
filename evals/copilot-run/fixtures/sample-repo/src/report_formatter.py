"""Formatting helpers for small report outputs."""


def _normalize_lines(lines: list[str]) -> list[str]:
    normalized = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            normalized.append(stripped)
    return normalized


def render_report(title: str, summary: str, items: list[str]) -> str:
    normalized_items = _normalize_lines(items)
    body = "\n".join(f"- {item}" for item in normalized_items)
    sections = [f"# {title}", "", summary.strip()]
    if body:
        sections.extend(["", "## Items", body])
    return "\n".join(sections).strip() + "\n"
