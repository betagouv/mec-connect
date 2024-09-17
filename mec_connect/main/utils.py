from __future__ import annotations


def str2bool(value: str) -> bool:
    """Convert a string value to a boolean value."""

    if value.lower() in ("yes", "true", "t", "1"):
        return True
    if value.lower() in ("no", "false", "f", "0"):
        return False
    raise ValueError(f"Invalid boolean value {value}")
