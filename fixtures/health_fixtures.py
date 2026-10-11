"""Fixtures health check - dane testowe sprawdzania dostępności usług."""

from typing import Any

import pytest

from utils.data_loader import load_test_data


@pytest.fixture(scope="session")
def health_check_data() -> dict[str, Any]:
	"""Wczytuje dane testowe health checków.

	Returns:
	    Zawartość pliku `test-data/health_checks.json`.
	"""
	return load_test_data("health_checks.json")
