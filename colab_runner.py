#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Colab/Local runner for the Meteo project.

- Ensures a sample input file exists (or lets user upload in Colab)
- Builds/updates the SQLite database
- Prints sample rows

This file is intentionally pure Python (no bash in notebook JSON) to avoid
Colab JSON parsing issues when embedded.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import List, Tuple


try:
    # Available only in Google Colab
    from google.colab import files  # type: ignore

    HAS_COLAB = True
except Exception:
    HAS_COLAB = False


DATA_FILENAME = "meteo_stat.txt"
DB_FILENAME = "BDDlite.db"
TABLE_NAME = "info_meteolite"


def ensure_input_file() -> Path:
    """Ensure input file exists via upload (Colab) or sample generation."""
    if HAS_COLAB:
        print("If you have a data file, upload it now (named 'meteo_stat.txt').")
        try:
            uploaded = files.upload()  # type: ignore
            if uploaded:
                uploaded_name = list(uploaded.keys())[0]
                if uploaded_name != DATA_FILENAME:
                    os.replace(uploaded_name, DATA_FILENAME)
                print(f"Uploaded file normalized to: {DATA_FILENAME}")
        except Exception as exc:
            print(f"Upload step skipped due to: {exc}")

    path = Path(DATA_FILENAME)
    if not path.exists():
        print("No upload detected. Creating a tiny sample 'meteo_stat.txt'...")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Header 1\n")
            f.write("Header 2\n")
            f.write("Header 3\n")
            f.write("2020-10-27 12:00\n")
            f.write("2020-10-27 13:00\n")
            f.write("2020-10-27 14:00\n")
    return path


def parse_input_lines(path: Path) -> List[Tuple[str, str]]:
    """Parse input lines after first 3 headers into (Date, Time) tuples."""
    rows: List[Tuple[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for index, line in enumerate(f):
            if index <= 2:
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                rows.append((parts[0], parts[1]))
    return rows


def build_database(rows: List[Tuple[str, str]]) -> None:
    connection = sqlite3.connect(DB_FILENAME)
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (Date TEXT, Time TEXT)"
        )
        cursor.executemany(
            f"INSERT INTO {TABLE_NAME} (Date, Time) VALUES (?, ?)", rows
        )
        connection.commit()
    finally:
        connection.close()


def query_all() -> List[Tuple[str, str]]:
    connection = sqlite3.connect(DB_FILENAME)
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT Date, Time FROM {TABLE_NAME}")
        return cursor.fetchall()
    finally:
        connection.close()


def main() -> None:
    input_path = ensure_input_file()
    print(f"Using input: {input_path}")
    rows = parse_input_lines(input_path)
    print(f"Parsed {len(rows)} rows")
    build_database(rows)
    print(f"Database '{DB_FILENAME}' updated. Table '{TABLE_NAME}'.")
    results = query_all()
    print("Sample rows:")
    for row in results[:10]:
        print(row)


if __name__ == "__main__":
    main()

