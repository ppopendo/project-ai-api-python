"""Fixtures konfiguracji testów."""

import pytest

from utils.config import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
	"""Zwraca konfigurację wczytaną ze zmiennych środowiskowych / pliku `.env`.

	Returns:
	    Obiekt `Settings` współdzielony przez całą sesję testową.
	"""
	return Settings.from_env()
