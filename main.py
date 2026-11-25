#!/usr/bin/env python3
"""Remove duplicate rows from a CSV file.

Two rows count as duplicates when their values match on the chosen
key columns (all columns by default). The first occurrence is kept
unless ``--keep last`` is used. A short report of how many rows
were removed is printed, and duplicates can be saved separately
with ``--duplicates-out``.
"""
import argparse
import csv
import sys


def dedupe(rows, columns, keep="first", case_insensitive=False):
    """Return (kept_rows, duplicate_rows) for *rows* (list of dicts)."""
    def key(row):
        values = [(row.get(col) or "") for col in columns]
        if case_insensitive:
            values = [value.lower() for value in values]
        return tuple(values)

    if keep == "last":
        # Walk backwards so the last occurrence wins, then restore order.
        seen, kept_reversed, dups = set(), [], []
        for row in reversed(rows):
            if key(row) in seen:
                dups.append(row)
            else:
                seen.add(key(row))
                kept_reversed.append(row)
        return list(reversed(kept_reversed)), list(reversed(dups))

    seen, kept, dups = set(), [], []
    for row in rows:
        if key(row) in seen:
            dups.append(row)
        else:
            seen.add(key(row))
            kept.append(row)
    return kept, dups


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Remove duplicate rows from a CSV file.")
    parser.add_argument("input", help="input CSV file")
    parser.add_argument("-o", "--output",
                        help="output CSV file (default: overwrite in place "
                             "only with --in-place, otherwise print to stdout)")
    parser.add_argument("--in-place", action="store_true",
                        help="write the deduplicated rows back to the input file")
    parser.add_argument("--columns",
                        help="comma-separated key columns to compare "
                             "(default: all columns)")
    parser.add_argument("--keep", choices=["first", "last"], default="first",
                        help="which duplicate to keep (default: first)")
    parser.add_argument("--case-insensitive", action="store_true",
                        help="ignore case when comparing values")
    parser.add_argument("--delimiter", default=",",
                        help="CSV field delimiter (default: ',')")
    parser.add_argument("--duplicates-out",
                        help="optional CSV file to save the removed rows in")
    args = parser.parse_args(argv)

    if args.output and args.in_place:
        parser.error("use either --output or --in-place, not both")
    try:
        with open(args.input, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter=args.delimiter)
            if reader.fieldnames is None:
                print(f"error: no header row found in {args.input}",
                      file=sys.stderr)
                return 1
            columns = [c.strip() for c in args.columns.split(",")] \
                if args.columns else list(reader.fieldnames)
            for col in columns:
                if col not in reader.fieldnames:
                    print(f"error: unknown column: {col}", file=sys.stderr)
                    return 1
            rows = list(reader)
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 1

    kept, dups = dedupe(rows, columns, keep=args.keep,
                        case_insensitive=args.case_insensitive)
    target = args.input if args.in_place else args.output
    handle = (open(target, "w", newline="", encoding="utf-8")
              if target else sys.stdout)
    try:
        writer = csv.DictWriter(handle, fieldnames=reader.fieldnames,
                                delimiter=args.delimiter)
        writer.writeheader()
        writer.writerows(kept)
    finally:
        if target:
            handle.close()
    if args.duplicates_out and dups:
        with open(args.duplicates_out, "w", newline="",
                  encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=reader.fieldnames,
                                    delimiter=args.delimiter)
            writer.writeheader()
            writer.writerows(dups)

    print(f"Removed {len(dups)} duplicate row(s); kept {len(kept)} of "
          f"{len(rows)} row(s)", file=sys.stderr if not target else sys.stdout)
    if target:
        print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
