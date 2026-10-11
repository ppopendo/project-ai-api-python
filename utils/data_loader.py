"""Wczytywanie danych testowych z katalogu `test-data`."""

import json
from pathlib import Path
from typing import Any

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test-data"


def load_test_data(file_name: str) -> dict[str, Any]:
	"""Wczytuje plik JSON z katalogu `test-data`.

	Args:
	    file_name: Nazwa pliku w katalogu `test-data`, np. `"stations.json"`.

	Returns:
	    Zawartość pliku jako słownik.

	Raises:
	    FileNotFoundError: Gdy plik nie istnieje.
	"""
	file_path = TEST_DATA_DIR / file_name
	with file_path.open(encoding="utf-8") as file:
		return json.load(file)
