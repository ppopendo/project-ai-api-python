"""Fixtures danych testowych pogody."""

from typing import Any

import pytest

from utils.data_loader import load_test_data


@pytest.fixture(scope="session")
def weather_test_data() -> dict[str, Any]:
	"""Wczytuje dane testowe pogody.

	Returns:
	    Zawartość pliku `test-data/weather.json`.
	"""
	return load_test_data("weather.json")
