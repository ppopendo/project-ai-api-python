"""Klient Current Weather Data API.

Dokumentacja: https://openweathermap.org/api/current
"""

import requests

from api.api_base import ApiBase, HealthStatus
from utils.config import Settings


class WeatherApi(ApiBase):
	"""Klient pobierający aktualną pogodę.

	Endpoint (bazowy URL: `{OPENWEATHER_BASE_URL}/data/2.5`):
	    * `GET /weather?q={miasto},{kod kraju}` - aktualna pogoda dla miasta (HTTP 200,
	      HTTP 404 gdy miasto nie zostało znalezione).
	"""

	API_VERSION_PATH = "/data/2.5"
	RESOURCE_PATH = "weather"

	def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
		"""Inicjalizuje klienta na podstawie konfiguracji.

		Args:
		    settings: Konfiguracja (bazowy URL, klucz API, timeout).
		    session: Opcjonalna sesja `requests`.
		"""
		super().__init__(
			base_url=f"{settings.base_url}{self.API_VERSION_PATH}",
			api_key=settings.api_key,
			timeout=settings.timeout,
			session=session,
		)

	def get_weather_by_city(
		self,
		city_name: str,
		country_code: str | None = None,
		units: str | None = None,
	) -> requests.Response:
		"""Pobiera aktualną pogodę dla wskazanego miasta.

		Args:
		    city_name: Nazwa miasta, np. `"Warsaw"`.
		    country_code: Opcjonalny kod kraju ISO 3166, np. `"PL"`.
		    units: Opcjonalne jednostki: `standard` (domyślne), `metric` lub `imperial`.

		Returns:
		    Odpowiedź serwera.
		"""
		query = f"{city_name},{country_code}" if country_code else city_name
		params = {"q": query}
		if units:
			params["units"] = units
		return self.get(self.RESOURCE_PATH, params=params)

	def check_health(self, probe_city: str) -> HealthStatus:
		"""Sprawdza, czy Current Weather Data API jest dostępne dla skonfigurowanego klucza.

		Args:
		    probe_city: Miasto użyte w zapytaniu kontrolnym.

		Returns:
		    `HealthStatus` z wynikiem sprawdzenia.
		"""
		return self._check_endpoint(self.RESOURCE_PATH, params={"q": probe_city})
