from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class WhereClause:
    column: str
    op: str
    value: str


def parse_select(select: str | None) -> list[str] | None:
    if not select:
        return None
    cols = [c.strip() for c in select.split(",") if c.strip()]
    return cols or None


def parse_where(where: str | None) -> WhereClause | None:
    """
    Supported operators: ==, !=, >=, <=, >, <
    Example: age>=18   or   country==Italy
    """
    if not where:
        return None
    ops = ["==", "!=", ">=", "<=", ">", "<"]
    for op in ops:
        if op in where:
            left, right = where.split(op, 1)
            col = left.strip()
            val = right.strip().strip('"').strip("'")
            if not col:
                raise ValueError("Invalid --where: missing column name")
            return WhereClause(column=col, op=op, value=val)
    raise ValueError("Invalid --where: operator not found (use ==, !=, >=, <=, >, <)")


def _to_number(s: str) -> float | None:
    try:
        return float(s)
    except Exception:
        return None


def row_matches(row: dict[str, str], clause: WhereClause) -> bool:
    raw = row.get(clause.column, "")
    left_num = _to_number(raw)
    right_num = _to_number(clause.value)

    # numeric compare if both are numbers, else string compare
    if left_num is not None and right_num is not None:
        a, b = left_num, right_num
    else:
        a, b = raw, clause.value

    op = clause.op
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    if op == ">=":
        return a >= b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == "<":
        return a < b
    raise ValueError(f"Unsupported operator: {op}")


def clean_csv(
    input_path: Path,
    output_path: Path,
    select: list[str] | None = None,
    where: WhereClause | None = None,
    dropna: bool = False,
    delimiter: str = ",",
) -> int:
    """
    Returns number of rows written (excluding header).
    """
    input_path = input_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with input_path.open("r", newline="", encoding="utf-8-sig") as f_in:
        reader = csv.DictReader(f_in, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row (fieldnames missing)")

        fieldnames = list(reader.fieldnames)

        if select:
            missing = [c for c in select if c not in fieldnames]
            if missing:
                raise ValueError(f"Selected columns not found in CSV: {missing}")
            out_fields = select
        else:
            out_fields = fieldnames

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=out_fields, delimiter=delimiter)
            writer.writeheader()

            written = 0
            for row in reader:
                if dropna:
                    # drop rows where any selected output field is empty
                    if any((row.get(c, "") or "").strip() == "" for c in out_fields):
                        continue

                if where and not row_matches(row, where):
                    continue

                writer.writerow({c: row.get(c, "") for c in out_fields})
                written += 1

    return written
