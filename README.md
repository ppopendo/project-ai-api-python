# project-ai-api-python

Projekt szkoleniowy - przygotowanie testów automatycznych w python z wykorzystaniem AI oraz pytest 🐛

Repozytorium pokazuje dobre praktyki tworzenia **automatycznych testów API typu CRUD** w Pythonie
z użyciem **pytest**, zgodnie z zasadą **AAA (Arrange – Act – Assert)**. Testowane jest publiczne
API [OpenWeatherMap](https://openweathermap.org/api):

| Grupa | Endpointy | Scenariusze |
|-------|-----------|-------------|
| [Weather Stations API 3.0](https://openweathermap.org/api/stations) | `POST/GET /data/3.0/stations`, `GET/PUT/DELETE /data/3.0/stations/{id}` | dodanie, pobranie (pojedyncza + lista), aktualizacja, usunięcie stacji |
| [Current Weather Data API](https://openweathermap.org/api/current) | `GET /data/2.5/weather?q={miasto},{kraj}` | pogoda dla miasta, nieistniejące miasto (404) |

Autoryzacja obu grup odbywa się parametrem query string `appid` (klucz API).

## Struktura projektu

```
.
├── .github/workflows/api-tests.yml  # CI: lint + format + testy API
├── api/                             # warstwa klientów API
│   ├── api_base.py                  # ApiBase: get/post/put/patch/delete, URL, nagłówki, appid, timeout, logi
│   ├── stations_api.py              # StationsApi(ApiBase) - CRUD stacji
│   └── weather_api.py               # WeatherApi(ApiBase) - aktualna pogoda
├── fixtures/                        # fixtures pytest
│   ├── config_fixtures.py           # konfiguracja testów
│   ├── client_fixtures.py           # klienci API
│   ├── health_fixtures.py           # dane testowe health checków
│   ├── station_fixtures.py          # dane stacji, setup/teardown stacji
│   └── weather_fixtures.py          # dane pogody
├── test-data/                       # dane testowe (JSON)
├── tests/
│   ├── conftest.py                  # rejestracja fixtures + obsługa unikalnych ID testów
│   ├── test_health_checks.py        # TC-HC-*
│   ├── test_stations_crud.py        # TC-STA-*
│   └── test_weather.py              # TC-WTH-*
├── utils/                           # konfiguracja (.env) i loader danych testowych
├── .env.example                     # nazwy zmiennych środowiskowych (bez wartości)
├── .pre-commit-config.yaml          # hooki pre-commit (ruff)
├── copilot-instructions.md          # instrukcje dla agenta Copilot
├── pyproject.toml                   # konfiguracja pytest i ruff
└── requirements.txt                 # zależności
```

Warstwy: **klient API** (`api/`) → **dane** (`test-data/`) → **fixtures** (`fixtures/`) → **testy** (`tests/`).

## Wymagania

- Python **3.11+**
- Konto OpenWeatherMap i klucz API: <https://home.openweathermap.org/api_keys>
  (darmowy plan wystarcza dla obu grup endpointów)

## Konfiguracja

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env    # Windows: copy .env.example .env
```

Uzupełnij plik `.env` (jest w `.gitignore` - **nigdy go nie commituj**). Wszystkie zmienne są
**wymagane** - brak którejkolwiek przerywa uruchomienie testów z czytelnym komunikatem:

| Zmienna | Wymagana | Przykład | Opis |
|---------|----------|----------|------|
| `OPENWEATHER_API_KEY` | tak | – | klucz API OpenWeatherMap |
| `OPENWEATHER_BASE_URL` | tak | `https://api.openweathermap.org` | bazowy adres API |
| `REQUEST_TIMEOUT` | tak | `10` | timeout żądania w sekundach |

Nie ma wartości domyślnych - konfiguracja pochodzi wyłącznie ze zmiennych środowiskowych.
Zmienne ustawione w systemie mają pierwszeństwo przed plikiem `.env`.

## Uruchomienie

```bash
# lint (standard kodowania, docstringi, importy, nazewnictwo)
ruff check .
# weryfikacja formatowania (bez zmian w plikach)
ruff format --check .
# automatyczne poprawki
ruff check --fix . && ruff format .

# wszystkie testy
pytest
# z raportami HTML i JUnit XML
pytest --html=reports/report.html --self-contained-html --junitxml=reports/junit.xml
# wybrane grupy (markery) lub pojedynczy test po ID
pytest -m health
pytest -m stations
pytest -k TC-STA-004
# podgląd logów żądań/odpowiedzi na żywo
pytest -o log_cli=true
```

Opcjonalnie pre-commit (lint + format przy każdym commicie):

```bash
pre-commit install
pre-commit run --all-files
```

## Jak działają testy

- **AAA** – każdy test ma sekcje `# Arrange`, `# Act`, `# Assert`.
- **Jeden test = jedna asercja** – testy nie zawierają instrukcji warunkowych (`if`) ani pętli.
  Gdy test sprawdza wiele wartości, buduje słownik `expected` (wartości oczekiwane) i słownik
  `actual` (wartości aktualne) i porównuje je pojedynczym `assert actual == expected`.
- **Unikalne ID** – każdy test ma marker `@pytest.mark.test_id("TC-XXX-NNN")`. `tests/conftest.py`
  przerywa uruchomienie, gdy ID brakuje lub się powtarza. ID trafia do logów, raportu JUnit
  (`<property name="test_id">`), kolumny „Test ID” raportu HTML i może być użyte w `pytest -k`.
- **Health checks** – `test_health_checks.py` sprawdza dostępność i autoryzację obu usług (test kończy
  się błędem, gdy usługa nie działa). Są to niezależne scenariusze - nie blokują ani nie pomijają
  pozostałych testów (brak bramek „service ready”, aby nie obciążać dodatkowo infrastruktury).
- **Niezależność i powtarzalność** – każda stacja dostaje unikalny `external_id`, a fixture
  `station_cleanup` usuwa utworzone stacje po teście (również gdy test się nie powiedzie).
- **Logowanie** – `ApiBase` loguje każde żądanie i odpowiedź; klucz API jest maskowany (`***`).

### Ograniczenia endpointów

| Sytuacja | Zachowanie testów |
|----------|-------------------|
| Brak którejkolwiek zmiennej (`OPENWEATHER_API_KEY`, `OPENWEATHER_BASE_URL`, `REQUEST_TIMEOUT`) | uruchomienie przerwane - testy nie startują (`pytest` kończy się błędem konfiguracji) |
| HTTP 401 – nowy klucz nie jest jeszcze aktywny (aktywacja może potrwać do kilku godzin), klucz nieprawidłowy lub usługa niedostępna w planie subskrypcji | test health check = FAILED, testy zależne wykonują się i również kończą się błędem (np. 401) |
| HTTP 429 – przekroczony limit zapytań planu | test health check = FAILED, pozostałe testy zwracają błąd 429 |
| Weather Stations API 3.0 ma status **beta** | jw. – niedostępność usługi skutkuje błędem testów CRUD |

## CI – GitHub Actions

Workflow [`.github/workflows/api-tests.yml`](.github/workflows/api-tests.yml) uruchamia się:

- ręcznie (`workflow_dispatch`),
- przy `push` do `main` (w tym po merge PR),
- dla `pull_request` celujących w `main`.

Kroki: setup Pythona → instalacja zależności → `ruff check` i `ruff format --check` → `pytest`
→ publikacja raportów (`reports/report.html`, `reports/junit.xml`) jako artefakt `api-test-report`.

Konfiguracja sekretu: **Settings → Secrets and variables → Actions → New repository secret**
o nazwie `OPENWEATHER_API_KEY`. Workflow przekazuje `OPENWEATHER_BASE_URL` i `REQUEST_TIMEOUT`
jako zmienne środowiskowe - z repozytoryjnych `Variables`, a przy ich braku z wartości zastępczych
(`https://api.openweathermap.org`, `10`). Gdy sekret jest niedostępny (np. PR z forka),
workflow wyświetla ostrzeżenie, a krok z testami API jest pomijany.

## Dodawanie nowych testów

1. Nowy endpoint → metoda w istniejącym kliencie lub nowa klasa dziedzicząca po `ApiBase` w `api/`.
2. Dane testowe → plik JSON w `test-data/`.
3. Fixtures (klient, dane, setup/teardown) → moduł w `fixtures/`
   dopisany do `pytest_plugins` w `tests/conftest.py`.
4. Test w `tests/test_*.py` – AAA, docstring, unikalny `@pytest.mark.test_id(...)`.
