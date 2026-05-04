"""Minimal path policy helpers."""


def normalize_paths(paths: list[str]) -> list[str]:
    """Normalize, dedupe, and sort repo-relative paths."""
    cleaned = {path.strip().strip("/") for path in paths if path and path.strip()}
    return sorted(path for path in cleaned if path)


def is_forbidden(path: str, forbidden_roots: list[str]) -> bool:
    normalized_path = path.strip().strip("/")
    for root in normalize_paths(forbidden_roots):
        if normalized_path == root or normalized_path.startswith(root + "/"):
            return True
    return False
