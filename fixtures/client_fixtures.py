"""Fixtures tworzące klientów API."""

from collections.abc import Iterator

import pytest

from api.stations_api import StationsApi
from api.weather_api import WeatherApi
from utils.config import Settings


@pytest.fixture(scope="session")
def stations_api(settings: Settings) -> Iterator[StationsApi]:
	"""Tworzy klienta Weather Stations API na całą sesję testową.

	Args:
	    settings: Konfiguracja testów.

	Yields:
	    Klient `StationsApi`; po zakończeniu sesji jego połączenia są zamykane.
	"""
	client = StationsApi(settings)
	yield client
	client.close()


@pytest.fixture(scope="session")
def weather_api(settings: Settings) -> Iterator[WeatherApi]:
	"""Tworzy klienta Current Weather Data API na całą sesję testową.

	Args:
	    settings: Konfiguracja testów.

	Yields:
	    Klient `WeatherApi`; po zakończeniu sesji jego połączenia są zamykane.
	"""
	client = WeatherApi(settings)
	yield client
	client.close()
