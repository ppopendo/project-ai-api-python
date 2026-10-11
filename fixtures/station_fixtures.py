"""Fixtures danych stacji oraz przygotowania i sprzątania stacji (setup/teardown)."""

import copy
import logging
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import pytest

from api.stations_api import StationsApi
from utils.data_loader import load_test_data

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreatedStation:
	"""Stacja utworzona na potrzeby testu.

	Attributes:
	    station_id: ID stacji nadane przez API.
	    payload: Dane, z którymi stacja została utworzona.
	"""

	station_id: str
	payload: dict[str, Any]


def with_unique_external_id(station: dict[str, Any]) -> dict[str, Any]:
	"""Zwraca kopię danych stacji z unikalnym `external_id`.

	Unikalny sufiks sprawia, że testy uruchamiane równolegle lub wielokrotnie
	nie kolidują ze sobą.

	Args:
	    station: Dane stacji wczytane z `test-data`.

	Returns:
	    Nowy słownik z `external_id` rozszerzonym o losowy sufiks.
	"""
	unique_station = copy.deepcopy(station)
	unique_station["external_id"] = f"{station['external_id']}_{uuid.uuid4().hex[:8]}"
	return unique_station


@pytest.fixture(scope="session")
def stations_test_data() -> dict[str, Any]:
	"""Wczytuje dane testowe stacji.

	Returns:
	    Zawartość pliku `test-data/stations.json`.
	"""
	return load_test_data("stations.json")


@pytest.fixture
def new_station_payload(stations_test_data: dict[str, Any]) -> dict[str, Any]:
	"""Zwraca dane nowej stacji z unikalnym `external_id`.

	Args:
	    stations_test_data: Dane testowe stacji.

	Returns:
	    Dane do utworzenia stacji.
	"""
	return with_unique_external_id(stations_test_data["new_station"])


@pytest.fixture
def updated_station_payload(stations_test_data: dict[str, Any]) -> dict[str, Any]:
	"""Zwraca dane do aktualizacji stacji z unikalnym `external_id`.

	Args:
	    stations_test_data: Dane testowe stacji.

	Returns:
	    Dane do aktualizacji stacji.
	"""
	return with_unique_external_id(stations_test_data["updated_station"])


@pytest.fixture
def station_cleanup(stations_api: StationsApi) -> Iterator[list[str]]:
	"""Rejestr ID stacji, które zostaną usunięte po zakończeniu testu (teardown).

	Test (lub inna fixture) dopisuje ID utworzonej stacji do zwróconej listy.
	Stacje już usunięte przez test (HTTP 404) są pomijane.

	Args:
	    stations_api: Klient Weather Stations API.

	Yields:
	    Lista ID stacji do usunięcia.
	"""
	station_ids: list[str] = []
	yield station_ids

	for station_id in station_ids:
		response = stations_api.delete_station(station_id)
		if response.status_code not in (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_FOUND):
			logger.warning(
				"Teardown: nie udało się usunąć stacji %s (HTTP %s).",
				station_id,
				response.status_code,
			)


@pytest.fixture
def created_station(
	stations_api: StationsApi,
	new_station_payload: dict[str, Any],
	station_cleanup: list[str],
) -> CreatedStation:
	"""Tworzy stację przed testem i rejestruje ją do usunięcia po teście.

	Args:
	    stations_api: Klient Weather Stations API.
	    new_station_payload: Dane nowej stacji.
	    station_cleanup: Rejestr stacji do usunięcia po teście.

	Returns:
	    `CreatedStation` z ID i danymi utworzonej stacji.
	"""
	response = stations_api.create_station(new_station_payload)
	assert response.status_code == HTTPStatus.CREATED, (
		f"Setup: nie udało się utworzyć stacji (HTTP {response.status_code}): {response.text}"
	)

	station_id = StationsApi.extract_station_id(response.json())
	assert station_id, f"Setup: odpowiedź nie zawiera ID stacji: {response.text}"
	station_cleanup.append(station_id)

	return CreatedStation(station_id=station_id, payload=new_station_payload)
