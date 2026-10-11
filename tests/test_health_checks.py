"""Health checks - weryfikacja, czy usługi API są dostępne i gotowe do testów.

Te testy kończą się błędem, gdy usługa nie działa (aby problem był widoczny w raporcie).
Nie blokują ani nie pomijają pozostałych testów - są niezależnymi scenariuszami.
"""

from typing import Any

import pytest

from api.stations_api import StationsApi
from api.weather_api import WeatherApi

pytestmark = [pytest.mark.health]


@pytest.mark.test_id("TC-HC-001")
def test_weather_service_is_available(
	weather_api: WeatherApi,
	health_check_data: dict[str, Any],
) -> None:
	"""Current Weather Data API odpowiada poprawnie dla skonfigurowanego klucza API."""
	# Arrange
	probe_city = health_check_data["weather_probe_city"]

	# Act
	status = weather_api.check_health(probe_city)

	# Assert
	assert status.is_available, status.reason


@pytest.mark.test_id("TC-HC-002")
def test_stations_service_is_available(stations_api: StationsApi) -> None:
	"""Weather Stations API odpowiada poprawnie dla skonfigurowanego klucza API."""
	# Arrange - klient `stations_api` przygotowany przez fixture

	# Act
	status = stations_api.check_health()

	# Assert
	assert status.is_available, status.reason
