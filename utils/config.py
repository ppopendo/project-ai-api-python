"""Konfiguracja testów wczytywana wyłącznie ze zmiennych środowiskowych (plik `.env`)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

REQUIRED_ENV_VARS = ("OPENWEATHER_API_KEY", "OPENWEATHER_BASE_URL", "REQUEST_TIMEOUT")


class MissingEnvironmentError(RuntimeError):
	"""Brak wymaganych zmiennych środowiskowych konfiguracji.

	Attributes:
	    missing: Nazwy zmiennych środowiskowych, których brakuje lub są puste.
	"""

	def __init__(self, missing: list[str]) -> None:
		"""Inicjalizuje wyjątek z listą brakujących zmiennych.

		Args:
		    missing: Nazwy brakujących lub pustych zmiennych środowiskowych.
		"""
		self.missing = missing
		super().__init__(
			"Brak wymaganych zmiennych środowiskowych: "
			+ ", ".join(missing)
			+ ". Ustaw je w pliku .env (zob. .env.example) - testy nie zostaną uruchomione."
		)


@dataclass(frozen=True)
class Settings:
	"""Ustawienia potrzebne do komunikacji z OpenWeatherMap API.

	Wszystkie wartości pochodzą wyłącznie ze zmiennych środowiskowych - brak wartości
	domyślnych. Gdy którejkolwiek zmiennej brakuje, `from_env` zgłasza wyjątek.

	Attributes:
	    api_key: Klucz API OpenWeatherMap (parametr `appid`).
	    base_url: Bazowy adres serwera API (bez wersji i ścieżki).
	    timeout: Maksymalny czas oczekiwania na odpowiedź serwera w sekundach.
	"""

	api_key: str
	base_url: str
	timeout: float

	@classmethod
	def from_env(cls) -> "Settings":
		"""Tworzy ustawienia na podstawie zmiennych środowiskowych.

		Najpierw wczytywany jest plik `.env` (jeśli istnieje). Zmienne już ustawione
		w systemie (np. sekrety GitHub Actions) mają pierwszeństwo przed plikiem `.env`.
		Wszystkie zmienne z `REQUIRED_ENV_VARS` są wymagane - brak którejkolwiek
		przerywa konfigurację.

		Returns:
		    Obiekt `Settings` z wartościami ze środowiska.

		Raises:
		    MissingEnvironmentError: Gdy którakolwiek wymagana zmienna jest pusta lub nieustawiona.
		"""
		load_dotenv(override=False)
		values = {name: (os.getenv(name) or "").strip() for name in REQUIRED_ENV_VARS}
		missing = [name for name, value in values.items() if not value]
		if missing:
			raise MissingEnvironmentError(missing)
		return cls(
			api_key=values["OPENWEATHER_API_KEY"],
			base_url=values["OPENWEATHER_BASE_URL"].rstrip("/"),
			timeout=float(values["REQUEST_TIMEOUT"]),
		)
