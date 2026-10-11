"""Klasa bazowa dla klientów REST API z ogólnymi metodami CRUD."""

import json
import logging
import time
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import requests

logger = logging.getLogger(__name__)

MASKED_VALUE = "***"
MAX_LOGGED_BODY_LENGTH = 1000


@dataclass(frozen=True)
class HealthStatus:
	"""Wynik sprawdzenia dostępności usługi (health check).

	Attributes:
	    is_available: True, jeśli usługa odpowiada poprawnie i autoryzacja działa.
	    reason: Czytelny opis wyniku - używany w asercjach i komunikatach `skip`.
	"""

	is_available: bool
	reason: str


class ApiBase:
	"""Ogólny klient HTTP z metodami CRUD, po którym dziedziczą konkretne klienty API.

	Odpowiada za:
	    * budowanie adresu URL na podstawie bazowego URL i ścieżki,
	    * dodawanie wspólnych nagłówków i klucza API (parametr `appid`),
	    * timeout każdego żądania,
	    * logowanie żądań i odpowiedzi (z zamaskowanym kluczem API).

	Aby dodać nowego klienta, utwórz klasę dziedziczącą po `ApiBase` i dodaj w niej
	metody biznesowe (np. `create_station`) korzystające z `get`/`post`/`put`/`patch`/`delete`.
	"""

	API_KEY_PARAM = "appid"
	DEFAULT_HEADERS = {"Accept": "application/json"}

	def __init__(
		self,
		base_url: str,
		api_key: str,
		timeout: float,
		session: requests.Session | None = None,
	) -> None:
		"""Inicjalizuje klienta.

		Args:
		    base_url: Bazowy adres API, np. `https://api.openweathermap.org/data/2.5`.
		    api_key: Klucz API dołączany do każdego żądania jako parametr `appid`.
		    timeout: Maksymalny czas oczekiwania na odpowiedź w sekundach.
		    session: Opcjonalna sesja `requests` (np. współdzielona); domyślnie tworzona nowa.
		"""
		self.base_url = base_url.rstrip("/")
		self.timeout = timeout
		self._api_key = api_key
		self.session = session or requests.Session()
		self.session.headers.update(self.DEFAULT_HEADERS)

	def get(self, path: str = "", params: dict[str, Any] | None = None) -> requests.Response:
		"""Wysyła żądanie GET (READ).

		Args:
		    path: Ścieżka względem bazowego URL, np. `"stations"`.
		    params: Dodatkowe parametry query string.

		Returns:
		    Odpowiedź serwera.
		"""
		return self.request("GET", path, params=params)

	def post(
		self,
		path: str = "",
		payload: dict[str, Any] | None = None,
		params: dict[str, Any] | None = None,
	) -> requests.Response:
		"""Wysyła żądanie POST (CREATE) z ciałem JSON.

		Args:
		    path: Ścieżka względem bazowego URL.
		    payload: Dane wysyłane w ciele żądania jako JSON.
		    params: Dodatkowe parametry query string.

		Returns:
		    Odpowiedź serwera.
		"""
		return self.request("POST", path, params=params, payload=payload)

	def put(
		self,
		path: str = "",
		payload: dict[str, Any] | None = None,
		params: dict[str, Any] | None = None,
	) -> requests.Response:
		"""Wysyła żądanie PUT (UPDATE - pełna aktualizacja zasobu) z ciałem JSON.

		Args:
		    path: Ścieżka względem bazowego URL.
		    payload: Dane wysyłane w ciele żądania jako JSON.
		    params: Dodatkowe parametry query string.

		Returns:
		    Odpowiedź serwera.
		"""
		return self.request("PUT", path, params=params, payload=payload)

	def patch(
		self,
		path: str = "",
		payload: dict[str, Any] | None = None,
		params: dict[str, Any] | None = None,
	) -> requests.Response:
		"""Wysyła żądanie PATCH (UPDATE - częściowa aktualizacja zasobu) z ciałem JSON.

		Args:
		    path: Ścieżka względem bazowego URL.
		    payload: Dane wysyłane w ciele żądania jako JSON.
		    params: Dodatkowe parametry query string.

		Returns:
		    Odpowiedź serwera.
		"""
		return self.request("PATCH", path, params=params, payload=payload)

	def delete(self, path: str = "", params: dict[str, Any] | None = None) -> requests.Response:
		"""Wysyła żądanie DELETE (DELETE).

		Args:
		    path: Ścieżka względem bazowego URL.
		    params: Dodatkowe parametry query string.

		Returns:
		    Odpowiedź serwera.
		"""
		return self.request("DELETE", path, params=params)

	def request(
		self,
		method: str,
		path: str = "",
		params: dict[str, Any] | None = None,
		payload: dict[str, Any] | None = None,
	) -> requests.Response:
		"""Wysyła żądanie HTTP - wspólna logika dla wszystkich metod CRUD.

		Args:
		    method: Metoda HTTP, np. `"GET"`.
		    path: Ścieżka względem bazowego URL.
		    params: Dodatkowe parametry query string (klucz API dodawany automatycznie).
		    payload: Opcjonalne ciało żądania wysyłane jako JSON.

		Returns:
		    Odpowiedź serwera.

		Raises:
		    requests.RequestException: Gdy nie udało się nawiązać połączenia lub minął timeout.
		"""
		url = self._build_url(path)
		query_params = {self.API_KEY_PARAM: self._api_key, **(params or {})}
		self._log_request(method, url, query_params, payload)

		started_at = time.perf_counter()
		try:
			response = self.session.request(
				method,
				url,
				params=query_params,
				json=payload,
				timeout=self.timeout,
			)
		except requests.RequestException as error:
			logger.error("%s %s failed: %s", method, url, self.mask_secrets(str(error)))
			raise
		elapsed_ms = (time.perf_counter() - started_at) * 1000

		self._log_response(response, elapsed_ms)
		return response

	def close(self) -> None:
		"""Zamyka sesję HTTP i zwalnia połączenia."""
		self.session.close()

	def mask_secrets(self, text: str) -> str:
		"""Zastępuje klucz API w tekście maską, aby nie wyciekł do logów ani raportów.

		Args:
		    text: Dowolny tekst (np. komunikat błędu zawierający URL).

		Returns:
		    Tekst z zamaskowanym kluczem API.
		"""
		if not self._api_key:
			return text
		return text.replace(self._api_key, MASKED_VALUE)

	def _check_endpoint(self, path: str, params: dict[str, Any] | None = None) -> HealthStatus:
		"""Sprawdza dostępność endpointu wykonując żądanie GET.

		Args:
		    path: Ścieżka sprawdzanego endpointu.
		    params: Dodatkowe parametry query string.

		Returns:
		    `HealthStatus` z informacją o dostępności i czytelnym powodem.
		"""
		url = self._build_url(path)
		try:
			response = self.get(path, params=params)
		except requests.RequestException as error:
			return HealthStatus(False, f"{url}: brak połączenia - {self.mask_secrets(str(error))}")

		if response.status_code == HTTPStatus.OK:
			return HealthStatus(True, f"{url}: usługa dostępna (HTTP 200).")
		if response.status_code == HTTPStatus.UNAUTHORIZED:
			return HealthStatus(
				False,
				f"{url}: HTTP 401 - nieprawidłowy/nieaktywny klucz API lub brak dostępu "
				"do tej usługi w Twoim planie subskrypcji.",
			)
		if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
			return HealthStatus(False, f"{url}: HTTP 429 - przekroczono limit zapytań.")
		return HealthStatus(
			False,
			f"{url}: nieoczekiwana odpowiedź HTTP {response.status_code} - "
			f"{self.mask_secrets(response.text[:200])}",
		)

	def _build_url(self, path: str) -> str:
		"""Łączy bazowy URL ze ścieżką endpointu.

		Args:
		    path: Ścieżka względem bazowego URL (z wiodącym `/` lub bez).

		Returns:
		    Pełny adres URL bez parametrów query string.
		"""
		return f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url

	def _log_request(
		self,
		method: str,
		url: str,
		params: dict[str, Any],
		payload: dict[str, Any] | None,
	) -> None:
		"""Loguje wysyłane żądanie z zamaskowanym kluczem API.

		Args:
		    method: Metoda HTTP.
		    url: Adres URL bez parametrów query string.
		    params: Parametry query string.
		    payload: Ciało żądania (lub None).
		"""
		safe_params = {
			key: MASKED_VALUE if key == self.API_KEY_PARAM else value
			for key, value in params.items()
		}
		logger.info("--> %s %s params=%s", method, url, safe_params)
		if payload is not None:
			logger.info("--> body: %s", json.dumps(payload, ensure_ascii=False))

	def _log_response(self, response: requests.Response, elapsed_ms: float) -> None:
		"""Loguje otrzymaną odpowiedź (status, czas i skrócone ciało).

		Args:
		    response: Odpowiedź serwera.
		    elapsed_ms: Czas trwania żądania w milisekundach.
		"""
		body = self.mask_secrets(response.text[:MAX_LOGGED_BODY_LENGTH])
		logger.info(
			"<-- %s %s (%.0f ms) body: %s",
			response.status_code,
			response.reason,
			elapsed_ms,
			body,
		)
