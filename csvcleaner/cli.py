from __future__ import annotations
import argparse
from pathlib import Path

from .core import clean_csv, parse_select, parse_where


def main() -> int:
    p = argparse.ArgumentParser(description="Clean/filter a CSV file (no pandas required).")
    p.add_argument("input", help="Path to input CSV")
    p.add_argument("output", help="Path to output CSV")
    p.add_argument("--select", default=None, help="Comma-separated columns to keep (e.g. name,age,country)")
    p.add_argument("--where", default=None, help='Filter like: age>=18 or country=="Italy"')
    p.add_argument("--dropna", action="store_true", help="Drop rows with empty values in selected columns")
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")

    args = p.parse_args()

    select = parse_select(args.select)
    where = parse_where(args.where)

    written = clean_csv(
        input_path=Path(args.input),
        output_path=Path(args.output),
        select=select,
        where=where,
        dropna=args.dropna,
        delimiter=args.delimiter,
    )
    print(f"[OK] Wrote {written} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
