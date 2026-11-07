"""Store one manual stats number with its date.

Usage: python3 stats/manual_entry.py <platform> <metric> <value> [--date YYYY-MM-DD] [--source manual:amir]

Every entry carries its source (who or what read the number): manual:amir by default,
cli:s4a-read or import:bandcamp-csv when a script typed it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stats import storage  # noqa: E402


def parse_value(raw: str):
    return float(raw) if "." in raw else int(raw)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Store a manual stats entry.")
    ap.add_argument("platform", choices=storage.MANUAL_PLATFORMS)
    ap.add_argument("metric")
    ap.add_argument("value", type=parse_value)
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--source", default="manual:amir", help="who read the number (default: manual:amir)")
    args = ap.parse_args(argv)
    entry = storage.save_manual_entry(args.platform, {args.metric: args.value}, date=args.date, source=args.source)
    print(json.dumps(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
