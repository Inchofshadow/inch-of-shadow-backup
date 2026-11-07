"""
release_manager/display.py
----------------------------
Print formatting utilities matching the project's CLI style.
"""

from __future__ import annotations

from datetime import datetime


def header(title: str, width: int = 40) -> None:
    """Print a section header: title + '=' underline."""
    print(f"\n{title}")
    print("=" * max(width, len(title)))


def section(name: str) -> None:
    """Print a subsection header like '  [Metadata]'."""
    print(f"\n  [{name}]")


def row(label: str, value: str, indent: int = 4, label_width: int = 18) -> None:
    """Print a label: value pair with alignment."""
    pad = " " * indent
    display = value if value else "\u2014"  # em-dash for empty
    print(f"{pad}{label + ':':<{label_width}} {display}")


def divider(width: int = 55, indent: int = 2) -> None:
    """Print a horizontal divider line."""
    print(" " * indent + "\u2500" * width)


def progress_bar(done: int, total: int, width: int = 10) -> str:
    """Return a text progress bar like '\u2588\u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591\u2591'."""
    if total == 0:
        return "\u2591" * width
    filled = round(width * done / total)
    return "\u2588" * filled + "\u2591" * (width - filled)


def days_until(date_str: str) -> str:
    """Return a human-readable string like 'in 31 days' or '3 days ago'."""
    if not date_str:
        return ""
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return ""
    delta = (target.date() - datetime.now().date()).days
    if delta == 0:
        return "today"
    if delta > 0:
        return f"in {delta} days"
    return f"{abs(delta)} days ago"


def check_mark(done: bool) -> str:
    """Return check or cross mark."""
    return "\u2713" if done else "\u2717"
