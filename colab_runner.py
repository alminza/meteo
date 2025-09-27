#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import sqlite3
from typing import List, Tuple

try:
	# Optional in Colab
	from google.colab import files  # type: ignore
	HAS_COLAB = True
except Exception:
	HAS_COLAB = False

DATA_FILENAME = "meteo_stat.txt"
DB_FILENAME = "BDDlite.db"
TABLE_NAME = "info_meteolite"


def ensure_input_file() -> Path:
	"""Ensure input file exists via upload or sample generation."""
	if HAS_COLAB:
		print("If you have a data file, upload it now (named 'meteo_stat.txt').")
		uploaded = files.upload()  # type: ignore
		if uploaded:
			uploaded_name = list(uploaded.keys())[0]
			if uploaded_name != DATA_FILENAME:
				os.replace(uploaded_name, DATA_FILENAME)
			print(f"Uploaded file normalized to: {DATA_FILENAME}")

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
	"""Parse the input file into (Date, Time) tuples.

	Assumes each relevant line (after first 3 headers) has "YYYY-MM-DD HH:MM".
	"""
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
	conn = sqlite3.connect(DB_FILENAME)
	try:
		cur = conn.cursor()
		cur.execute(
			f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (Date TEXT, Time TEXT)"
		)
		cur.executemany(
			f"INSERT INTO {TABLE_NAME} (Date, Time) VALUES (?, ?)", rows
		)
		conn.commit()
	finally:
		conn.close()


def query_all() -> List[Tuple[str, str]]:
	conn = sqlite3.connect(DB_FILENAME)
	try:
		cur = conn.cursor()
		cur.execute(f"SELECT Date, Time FROM {TABLE_NAME}")
		return cur.fetchall()
	finally:
		conn.close()


def main() -> None:
	input_path = ensure_input_file()
	print(f"Using input: {input_path}")
	rows = parse_input_lines(input_path)
	print(f"Parsed {len(rows)} rows")
	build_database(rows)
	print(f"Database '{DB_FILENAME}' updated. Table '{TABLE_NAME}'.")
	results = query_all()
	print("Sample rows:")
	for r in results[:10]:
		print(r)


if __name__ == "__main__":
	main()