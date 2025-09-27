import argparse
import os
import sqlite3
from typing import List, Sequence, Tuple


def read_temperature_lines(file_path: str, skip_header_lines: int = 3) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    with open(file_path, "r") as file_handle:
        for line_index, line in enumerate(file_handle):
            if line_index < skip_header_lines:
                continue
            tokens: List[str] = line.split()
            if len(tokens) >= 2:
                rows.append((tokens[0], tokens[1]))
    return rows


def ensure_table_exists(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS info_meteolite (Date TEXT, Time TEXT)"
    )


def insert_rows(cursor: sqlite3.Cursor, rows: Sequence[Tuple[str, str]]) -> int:
    cursor.executemany("INSERT INTO info_meteolite VALUES (?, ?)", rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Insert meteorological data into SQLite.")
    parser.add_argument("--file", default=os.path.join("data", "meteo_stat.txt"), help="Path to the input text file.")
    parser.add_argument("--db", default="BDDlite.db", help="SQLite database file path.")
    parser.add_argument("--skip-header", type=int, default=3, help="Number of header lines to skip.")
    args = parser.parse_args()

    rows: List[Tuple[str, str]] = read_temperature_lines(args.file, args.skip_header)
    with sqlite3.connect(args.db) as connection:
        cursor = connection.cursor()
        ensure_table_exists(cursor)
        num_inserted: int = insert_rows(cursor, rows)
        connection.commit()
    print(f"Inserted {num_inserted} rows into info_meteolite from {args.file}")


if __name__ == "__main__":
    main()