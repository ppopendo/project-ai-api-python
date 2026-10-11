"""Testy CRUD Weather Stations API: dodanie, pobranie, aktualizacja i usunięcie stacji."""

from http import HTTPStatus
from typing import Any

import pytest

from api.stations_api import StationsApi
from fixtures.station_fixtures import CreatedStation

pytestmark = [pytest.mark.stations]


def station_view(station: dict[str, Any]) -> dict[str, Any]:
	"""Wyodrębnia porównywane pola stacji z odpowiedzi API.

	Args:
	    station: Stacja zwrócona przez API.

	Returns:
	    Słownik z wartościami aktualnymi pól stacji.
	"""
	return {
		"external_id": station.get("external_id"),
		"name": station.get("name"),
		"latitude": station.get("latitude"),
		"longitude": station.get("longitude"),
		"altitude": station.get("altitude"),
	}


def expected_station(payload: dict[str, Any], tolerance: float) -> dict[str, Any]:
	"""Buduje oczekiwane pola stacji (współrzędne i wysokość z tolerancją).

	Args:
	    payload: Dane, z którymi stacja została utworzona lub zaktualizowana.
	    tolerance: Dopuszczalna różnica współrzędnych i wysokości.

	Returns:
	    Słownik z wartościami oczekiwanymi pól stacji.
	"""
	return {
		"external_id": payload["external_id"],
		"name": payload["name"],
		"latitude": pytest.approx(payload["latitude"], abs=tolerance),
		"longitude": pytest.approx(payload["longitude"], abs=tolerance),
		"altitude": pytest.approx(payload["altitude"], abs=tolerance),
	}


@pytest.mark.test_id("TC-STA-001")
def test_add_station(
	stations_api: StationsApi,
	new_station_payload: dict[str, Any],
	station_cleanup: list[str],
	stations_test_data: dict[str, Any],
) -> None:
	"""Utworzenie stacji zwraca HTTP 201, ID stacji oraz przesłane dane."""
	# Arrange
	tolerance = stations_test_data["coordinates_tolerance"]

	# Act
	response = stations_api.create_station(new_station_payload)
	created = response.json()
	station_id = StationsApi.extract_station_id(created)
	station_cleanup.append(station_id)

	# Assert
	expected = {
		"status_code": HTTPStatus.CREATED,
		"has_station_id": True,
		**expected_station(new_station_payload, tolerance),
	}
	actual = {
		"status_code": response.status_code,
		"has_station_id": bool(station_id),
		**station_view(created),
	}
	assert actual == expected


@pytest.mark.test_id("TC-STA-002")
def test_get_station(
	stations_api: StationsApi,
	created_station: CreatedStation,
	stations_test_data: dict[str, Any],
) -> None:
	"""Pobranie stacji po ID zwraca HTTP 200 i dane, z którymi stacja została utworzona."""
	# Arrange
	tolerance = stations_test_data["coordinates_tolerance"]

	# Act
	response = stations_api.get_station(created_station.station_id)
	station = response.json()

	# Assert
	expected = {
		"status_code": HTTPStatus.OK,
		"station_id": created_station.station_id,
		**expected_station(created_station.payload, tolerance),
	}
	actual = {
		"status_code": response.status_code,
		"station_id": StationsApi.extract_station_id(station),
		**station_view(station),
	}
	assert actual == expected


@pytest.mark.test_id("TC-STA-003")
def test_get_stations_list_contains_created_station(
	stations_api: StationsApi,
	created_station: CreatedStation,
) -> None:
	"""Lista stacji użytkownika zawiera utworzoną stację."""
	# Arrange - stacja przygotowana przez fixture `created_station`

	# Act
	response = stations_api.get_stations()
	station_ids = StationsApi.extract_station_ids(response.json())

	# Assert
	expected = {"status_code": HTTPStatus.OK, "contains_created_station": True}
	actual = {
		"status_code": response.status_code,
		"contains_created_station": created_station.station_id in station_ids,
	}
	assert actual == expected


@pytest.mark.test_id("TC-STA-004")
def test_update_station(
	stations_api: StationsApi,
	created_station: CreatedStation,
	updated_station_payload: dict[str, Any],
	stations_test_data: dict[str, Any],
) -> None:
	"""Aktualizacja stacji zwraca HTTP 200, a zmiany są widoczne przy ponownym pobraniu."""
	# Arrange
	tolerance = stations_test_data["coordinates_tolerance"]

	# Act
	update_response = stations_api.update_station(
		created_station.station_id, updated_station_payload
	)
	stored_response = stations_api.get_station(created_station.station_id)

	# Assert
	expected = {
		"update_status": HTTPStatus.OK,
		"stored_status": HTTPStatus.OK,
		"updated_station": expected_station(updated_station_payload, tolerance),
		"stored_station": expected_station(updated_station_payload, tolerance),
	}
	actual = {
		"update_status": update_response.status_code,
		"stored_status": stored_response.status_code,
		"updated_station": station_view(update_response.json()),
		"stored_station": station_view(stored_response.json()),
	}
	assert actual == expected


@pytest.mark.test_id("TC-STA-005")
def test_delete_station(stations_api: StationsApi, created_station: CreatedStation) -> None:
	"""Usunięcie stacji zwraca HTTP 204, a stacja przestaje istnieć (HTTP 404)."""
	# Arrange - stacja przygotowana przez fixture `created_station`

	# Act
	delete_response = stations_api.delete_station(created_station.station_id)
	get_response = stations_api.get_station(created_station.station_id)

	# Assert
	expected = {
		"delete_status": HTTPStatus.NO_CONTENT,
		"get_after_delete_status": HTTPStatus.NOT_FOUND,
	}
	actual = {
		"delete_status": delete_response.status_code,
		"get_after_delete_status": get_response.status_code,
	}
	assert actual == expected
