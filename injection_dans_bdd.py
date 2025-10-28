#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone ingestion script: parse a whitespace-delimited text file containing
weather data and insert (Date, Time) into a SQLite database.

This version has no dependency on any other files in the repository.
"""

import argparse
import os
import sqlite3
import sys
from typing import Iterable, List, Tuple


def read_rows(file_path: str, header_lines_to_skip: int, encoding: str) -> List[Tuple[str, str]]:
    """Read the input file and return a list of (Date, Time) tuples.

    Lines are split on whitespace. Blank lines are ignored. Only rows with at
    least two fields are considered.
    """
    final_rows: List[Tuple[str, str]] = []
    with open(file_path, 'r', encoding=encoding) as f:
        for index, line in enumerate(f):
            if index < header_lines_to_skip:
                continue
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) < 2:
                continue
            final_rows.append((parts[0], parts[1]))
    return final_rows


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (Date TEXT, Time TEXT)")


def insert_rows(conn: sqlite3.Connection, table_name: str, rows: Iterable[Tuple[str, str]]) -> int:
    cur = conn.cursor()
    data = list(rows)
    if not data:
        return 0
    cur.executemany(f"INSERT INTO {table_name} (Date, Time) VALUES (?, ?)", data)
    conn.commit()
    return cur.rowcount if cur.rowcount is not None else 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Insert (Date, Time) rows from a text file into a SQLite DB.")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to input text file",
    )
    parser.add_argument(
        "-d",
        "--database",
        default="BDDlite.db",
        help="Path to SQLite database file (default: BDDlite.db)",
    )
    parser.add_argument(
        "-t",
        "--table",
        default="info_meteolite",
        help="Table name to insert into (default: info_meteolite)",
    )
    parser.add_argument(
        "-s",
        "--skip",
        type=int,
        default=3,
        help="Number of header lines to skip (default: 3)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    rows = read_rows(args.input, args.skip, args.encoding)
    if not rows:
        print("No data rows found to insert.", file=sys.stderr)
        return 1

    conn = sqlite3.connect(args.database)
    try:
        ensure_table(conn, args.table)
        inserted = insert_rows(conn, args.table, rows)
    finally:
        conn.close()

    print(f"Inserted {inserted} rows into {args.database}.{args.table}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

