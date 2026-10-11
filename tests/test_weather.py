"""Testy Current Weather Data API: pobranie aktualnej pogody dla miasta."""

from http import HTTPStatus
from typing import Any

import pytest

from api.weather_api import WeatherApi

pytestmark = [pytest.mark.weather]


@pytest.mark.test_id("TC-WTH-001")
def test_get_weather_by_city(weather_api: WeatherApi, weather_test_data: dict[str, Any]) -> None:
	"""Pogoda dla istniejącego miasta zwraca HTTP 200 i kluczowe pola odpowiedzi."""
	# Arrange
	city = weather_test_data["city"]
	expected_coordinates = city["expected_coordinates"]
	tolerance = city["coordinates_tolerance"]
	temperature_range = city["temperature_range_celsius"]

	# Act
	response = weather_api.get_weather_by_city(
		city_name=city["name"],
		country_code=city["country_code"],
		units=city["units"],
	)
	body = response.json()
	main = body.get("main", {})
	weather_entries = body.get("weather", [])

	# Assert
	expected = {
		"status_code": HTTPStatus.OK,
		"name": city["name"],
		"country": city["country_code"],
		"lat": pytest.approx(expected_coordinates["lat"], abs=tolerance),
		"lon": pytest.approx(expected_coordinates["lon"], abs=tolerance),
		"temperature_in_range": True,
		"has_humidity": True,
		"has_weather_description": True,
	}
	actual = {
		"status_code": response.status_code,
		"name": body.get("name"),
		"country": body.get("sys", {}).get("country"),
		"lat": body.get("coord", {}).get("lat"),
		"lon": body.get("coord", {}).get("lon"),
		"temperature_in_range": temperature_range["min"]
		<= main.get("temp", float("nan"))
		<= temperature_range["max"],
		"has_humidity": "humidity" in main,
		"has_weather_description": bool(weather_entries) and "description" in weather_entries[0],
	}
	assert actual == expected


@pytest.mark.test_id("TC-WTH-002")
def test_get_weather_for_unknown_city_returns_not_found(
	weather_api: WeatherApi,
	weather_test_data: dict[str, Any],
) -> None:
	"""Zapytanie o nieistniejące miasto zwraca HTTP 404 z komunikatem błędu."""
	# Arrange
	unknown_city = weather_test_data["unknown_city"]

	# Act
	response = weather_api.get_weather_by_city(city_name=unknown_city["name"])

	# Assert
	expected = {
		"status_code": HTTPStatus.NOT_FOUND,
		"message": unknown_city["expected_message"],
	}
	actual = {
		"status_code": response.status_code,
		"message": response.json().get("message"),
	}
	assert actual == expected
