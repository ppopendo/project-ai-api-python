"""Klient Weather Stations API 3.0 (CRUD na stacjach pogodowych).

Dokumentacja: https://openweathermap.org/api/stations
"""

from typing import Any

import requests

from api.api_base import ApiBase, HealthStatus
from utils.config import Settings


class StationsApi(ApiBase):
	"""Klient zarządzający stacjami pogodowymi użytkownika.

	Endpointy (bazowy URL: `{OPENWEATHER_BASE_URL}/data/3.0`):
	    * `POST   /stations`       - utworzenie stacji (HTTP 201),
	    * `GET    /stations`       - lista stacji użytkownika (HTTP 200),
	    * `GET    /stations/{id}`  - pojedyncza stacja (HTTP 200),
	    * `PUT    /stations/{id}`  - aktualizacja stacji (HTTP 200),
	    * `DELETE /stations/{id}`  - usunięcie stacji (HTTP 204).
	"""

	API_VERSION_PATH = "/data/3.0"
	RESOURCE_PATH = "stations"

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

	def create_station(self, station: dict[str, Any]) -> requests.Response:
		"""Tworzy nową stację pogodową.

		Args:
		    station: Dane stacji: `external_id`, `name`, `latitude`, `longitude`, `altitude`.

		Returns:
		    Odpowiedź serwera (oczekiwany status 201, ID stacji w polu `ID`).
		"""
		return self.post(self.RESOURCE_PATH, payload=station)

	def get_stations(self) -> requests.Response:
		"""Pobiera listę wszystkich stacji użytkownika.

		Returns:
		    Odpowiedź serwera (oczekiwany status 200, lista stacji w ciele).
		"""
		return self.get(self.RESOURCE_PATH)

	def get_station(self, station_id: str) -> requests.Response:
		"""Pobiera pojedynczą stację po jej ID.

		Args:
		    station_id: Wewnętrzne ID stacji nadane przez OpenWeatherMap.

		Returns:
		    Odpowiedź serwera (200 dla istniejącej stacji, 404 gdy nie istnieje).
		"""
		return self.get(self._station_path(station_id))

	def update_station(self, station_id: str, station: dict[str, Any]) -> requests.Response:
		"""Aktualizuje dane istniejącej stacji.

		Args:
		    station_id: Wewnętrzne ID stacji.
		    station: Nowe dane stacji (te same pola co przy tworzeniu).

		Returns:
		    Odpowiedź serwera (oczekiwany status 200 i zaktualizowana stacja w ciele).
		"""
		return self.put(self._station_path(station_id), payload=station)

	def delete_station(self, station_id: str) -> requests.Response:
		"""Usuwa stację.

		Args:
		    station_id: Wewnętrzne ID stacji.

		Returns:
		    Odpowiedź serwera (oczekiwany status 204 bez ciała).
		"""
		return self.delete(self._station_path(station_id))

	def check_health(self) -> HealthStatus:
		"""Sprawdza, czy Weather Stations API jest dostępne dla skonfigurowanego klucza.

		Returns:
		    `HealthStatus` z wynikiem sprawdzenia.
		"""
		return self._check_endpoint(self.RESOURCE_PATH)

	@staticmethod
	def extract_station_id(station: dict[str, Any]) -> str | None:
		"""Zwraca ID stacji z odpowiedzi API.

		Odpowiedź na utworzenie stacji zwraca ID w polu `ID`, a odpowiedzi GET/PUT w polu `id`.

		Args:
		    station: Ciało odpowiedzi API opisujące stację.

		Returns:
		    ID stacji lub None, jeśli odpowiedź go nie zawiera.
		"""
		return station.get("ID") or station.get("id")

	@staticmethod
	def extract_station_ids(stations: list[dict[str, Any]]) -> list[str | None]:
		"""Zwraca listę ID stacji z odpowiedzi zawierającej listę stacji.

		Args:
		    stations: Lista stacji zwrócona przez endpoint listy stacji.

		Returns:
		    Lista ID stacji (None dla stacji bez identyfikatora).
		"""
		return [StationsApi.extract_station_id(station) for station in stations]

	def _station_path(self, station_id: str) -> str:
		"""Buduje ścieżkę do pojedynczej stacji.

		Args:
		    station_id: Wewnętrzne ID stacji.

		Returns:
		    Ścieżka w formacie `stations/{station_id}`.
		"""
		return f"{self.RESOURCE_PATH}/{station_id}"
