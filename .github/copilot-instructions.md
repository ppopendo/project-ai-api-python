# Copilot instructions – project-ai-api-python

## Opis projektu

- **Cel:** publiczne repozytorium szkoleniowe pokazujące dobre praktyki automatycznych testów API
  typu CRUD w Pythonie. Kod ma być prosty dla początkujących i łatwy w rozbudowie.
- **Zakres:**
  - Weather Stations API 3.0 (`/data/3.0/stations`) – dodanie, pobranie, aktualizacja, usunięcie stacji.
  - Current Weather Data API (`/data/2.5/weather`) – pogoda dla miasta.
  - Health checks dostępności obu usług.
- **Stack:** Python 3.11+, pytest, requests, python-dotenv, pytest-html, ruff (lint + format),
  pre-commit, GitHub Actions.
- **Poza zakresem:** testy jednostkowe – nie dodawaj ich.

## Architektura

| Warstwa | Katalog | Zasada |
|---------|---------|--------|
| Klienci API | `../api` | Każdy klient dziedziczy po `ApiBase` i używa jej metod `get/post/put/patch/delete`. Nie wywołuj `requests` bezpośrednio w testach ani fixtures. |
| Dane testowe | `../test-data` | Pliki JSON ładowane przez `utils.data_loader.load_test_data`. Żadnych „magicznych” wartości w testach. |
| Fixtures | `../fixtures` | Moduły rejestrowane w `pytest_plugins` w `../tests/conftest.py`. Setup/teardown zasobów przez `yield`. |
| Testy | `../tests` | Pliki `test_*.py`, wyłącznie testy API. |
| Konfiguracja | `../utils/config.py` | `Settings.from_env()` – jedyne miejsce odczytu zmiennych środowiskowych. |

## Standard kodowania

- **AAA:** każdy test zawiera komentarze `# Arrange`, `# Act`, `# Assert` (pustą sekcję opisz,
  np. `# Arrange - stacja przygotowana przez fixture`).
- **Unikalny ID testu:** każdy test ma `@pytest.mark.test_id("TC-<OBSZAR>-<NNN>")`, np. `TC-STA-006`.
  Obszary: `HC` (health check), `STA` (stacje), `WTH` (pogoda). ID nie mogą się powtarzać –
  `../tests/conftest.py` przerywa uruchomienie w razie braku lub duplikatu.
- **Docstringi:** każdy moduł, klasa, metoda, funkcja i fixture ma docstring w stylu Google
  (`Args:`, `Returns:`, `Yields:`, `Raises:`). Wymusza to ruff (reguły `D`).
- **Nazewnictwo:** opisowe nazwy w `snake_case` (funkcje, zmienne, fixtures) i `PascalCase` (klasy);
  testy: `test_<akcja>_<oczekiwany_rezultat>`.
- **Statusy HTTP:** używaj `http.HTTPStatus` (np. `HTTPStatus.CREATED`), nie liczb.
- **Niezależność testów:** zasoby tworzone w teście rejestruj do usunięcia (`station_cleanup`) lub
  używaj fixture tworzącej zasób z teardownem (`created_station`). Unikalne wartości generuj w fixtures.
- **Jedna asercja na test:** testy nie zawierają instrukcji `if` ani pętli. Gdy test sprawdza wiele
  wartości, buduj słownik `expected` i słownik `actual`, po czym porównaj je pojedynczym
  `assert actual == expected` (ewentualne iteracje/warunki przenieś do klienta API lub helpera).
- **Dostępność usług:** health checks (`TC-HC-*`) to niezależne testy; nie ma bramek `*_service_ready`
  pomijających testy funkcjonalne (aby nie obciążać dodatkowo infrastruktury).
- **Formatowanie i lint:** `ruff check .` oraz `ruff format --check .` muszą przechodzić
  (konfiguracja w `../pyproject.toml`, długość linii 100). Przed commitem: `pre-commit run --all-files`.
- **Komentarze:** tylko tam, gdzie kod wymaga wyjaśnienia.

## Credentials / Access

- Klucz API OpenWeatherMap: załóż konto na <https://home.openweathermap.org/users/sign_up> i skopiuj
  klucz z <https://home.openweathermap.org/api_keys>. Nowy klucz może aktywować się do kilku godzin
  (do tego czasu API zwraca HTTP 401).
- **Lokalnie:** skopiuj `../.env.example` do `../.env` i ustaw **wszystkie** zmienne:
  `OPENWEATHER_API_KEY`, `OPENWEATHER_BASE_URL`, `REQUEST_TIMEOUT`. Nie ma wartości domyślnych -
  brak którejkolwiek zmiennej przerywa uruchomienie testów (`Settings.from_env` zgłasza błąd).
- **CI:** sekret repozytorium `OPENWEATHER_API_KEY` (Settings → Secrets and variables → Actions),
  przekazywany do kroku testów jako zmienna środowiskowa.
- **Nigdy nie commituj:** pliku `../.env`, kluczy API, tokenów ani raportów z katalogu `reports/`.
  Nie wpisuj sekretów w kod, dane testowe, logi, komunikaty asercji ani dokumentację.
- Klucz jest dodawany do żądań wyłącznie przez `ApiBase` i maskowany w logach (`***`) –
  nie loguj pełnych adresów URL z parametrami (`response.url`).
- Nowe zmienne środowiskowe dodawaj jednocześnie do `../utils/config.py`, `../.env.example` (bez wartości),
  `../README.md` i workflow `workflows/api-tests.yml`.
