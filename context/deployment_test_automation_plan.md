### Rola

Jesteś doświadczonym inżynierem automatyzacji testów (SDET) specjalizującym się w testach API w Pythonie.
Twoim zadaniem jest zbudowanie **publicznego repozytorium szkoleniowego**, które pokazuje dobre praktyki
tworzenia **automatycznych testów API typu CRUD** z wykorzystaniem **Pythona i frameworka pytest**,
zgodnie z zasadą **AAA (Arrange – Act – Assert)**.

Kod ma być **prosty i czytelny dla osób rozpoczynających przygodę z automatyzacją testów**, a jednocześnie
**łatwy w utrzymaniu i rozbudowie**.

### Kontekst — API

Korzystasz z publicznej dokumentacji OpenWeatherMap API: https://openweathermap.org/api

Testujemy dwie grupy funkcjonalności:

1. **Weather Stations API** (CRUD na stacjach pogodowych — wymaga klucza API):
   - Dodanie stacji (CREATE)
   - Aktualizacja stacji (UPDATE)
   - Wyszukanie / pobranie stacji (READ — pojedyncza i/lub lista)
   - Usunięcie stacji (DELETE)
2. **Current Weather Data API**:
   - Wyszukanie pogody dla określonego miasta (np. po nazwie miasta)

> Uwaga dla agenta: przed implementacją **zweryfikuj w dokumentacji** aktualne ścieżki endpointów,
> wymagane parametry, metody HTTP oraz sposób autoryzacji (parametr `appid` / klucz API) dla obu grup.
> Jeśli któryś endpoint wymaga konkretnego planu subskrypcji, odnotuj to w `README.md`. Health checks
> są niezależnymi testami i **nie** pomijają pozostałych testów (brak bramek „service ready”, aby
> nie generować dodatkowego obciążenia infrastruktury).

### Zakres testów (scenariusze)

Zaimplementuj co najmniej następujące testy end-to-end API:

- **Stacje (CRUD)**:
  - `add_station` — utworzenie stacji i walidacja odpowiedzi (status, ID stacji, pola).
  - `update_station` — aktualizacja istniejącej stacji i walidacja zmiany.
  - `get_station` — pobranie/wyszukanie stacji i walidacja zwróconych danych.
  - `delete_station` — usunięcie stacji i walidacja, że przestała istnieć.
- **Pogoda**:
  - `get_weather_by_city` — pobranie pogody dla określonego miasta i walidacja kluczowych pól odpowiedzi.

Każdy scenariusz CRUD powinien po sobie sprzątać (teardown) — utworzone dane testowe mają być usuwane,
aby testy były **powtarzalne i niezależne**.

### Wymagania funkcjonalne i strukturalne

1. **Zasada AAA** — każdy test jasno podzielony na sekcje Arrange / Act / Assert (komentarzami lub strukturą).
2. **Jedna asercja na test, bez logiki w teście** — testy **nie zawierają** instrukcji warunkowych (`if`)
   ani pętli. Gdy test weryfikuje wiele wartości, buduje słownik z wartościami **oczekiwanymi**
   (`expected`) oraz słownik z wartościami **aktualnymi** (`actual`) i porównuje je jednym
   `assert actual == expected`. Ewentualne iteracje/warunki przenieś do klienta API lub funkcji pomocniczej.
3. **Health Checks** — przygotuj testy sprawdzające, czy wykorzystywane usługi (endpointy API)
   odpowiadają poprawnie (dostępność serwera, poprawność autoryzacji). Health checks są **niezależnymi
   testami** — nie pomijają ani nie blokują pozostałych testów. **Nie** dodawaj bramek typu
   `*_service_ready` weryfikujących dostępność usługi przed każdym testem — generują dodatkowe
   obciążenie infrastruktury i nie są wymagane.
4. **Klasa bazowa `ApiBase`** — utwórz klasę (np. `ApiBase`) zawierającą **ogólne metody HTTP na potrzeby CRUD**
   (`get`, `post`, `put`/`patch`, `delete`), obsługę bazowego URL, nagłówków, autoryzacji, timeoutów i logowania
   żądań/odpowiedzi. Konkretne klienty (np. `StationsApi`, `WeatherApi`) mają po niej dziedziczyć.
5. **Dane testowe** — zapisane w folderze **`test-data`** (np. pliki JSON) i ładowane do testów
   (żadnych „magicznych” wartości wklejanych w kodzie testów).
6. **Fixtures** — zapisane w folderze **`fixtures`** (fixtures pytest: m.in. klient API, dane stacji,
   setup/teardown zasobów, konfiguracja). Fixtures udostępnione testom przez `conftest.py`.
7. **Dokumentacja kodu** — **każda klasa i każda metoda** musi mieć czytelny docstring (po co jest,
   parametry, zwracana wartość). Nazewnictwo jasne i opisowe.
8. **Unikalny identyfikator testu** — **każdy test** powinien mieć unikalny identyfikator
   (np. marker/ID w nazwie lub dekorator), umożliwiający jednoznaczne wskazanie testu w raportach/logach.
9. **Bezpieczeństwo i konfiguracja przez zmienne środowiskowe** — klucz API i inne sekrety **nigdy nie
   trafiają do repozytorium**. Konfiguracja (`OPENWEATHER_API_KEY`, `OPENWEATHER_BASE_URL`,
   `REQUEST_TIMEOUT`) pochodzi **wyłącznie** ze zmiennych środowiskowych (przez `python-dotenv` + plik
   `.env` w `.gitignore`) — **bez wartości domyślnych w kodzie**. Gdy którejkolwiek zmiennej brakuje,
   **nie uruchamiaj testów** (przerwij z czytelnym komunikatem). Dodaj plik przykładowy **`.env.example`**
   z nazwami zmiennych bez wartości. W CI sekrety pobierane są z **GitHub Actions Secrets**.
10. **Prostota i rozbudowa** — architektura ma ułatwiać dodawanie nowych klientów API i testów
   (czytelny podział na warstwy: klient API / dane / fixtures / testy).

### Jakość kodu i standardy

- **Formatowanie i lint**: dodaj mechanizm weryfikacji formatowania oraz zgodności ze standardem kodowania.
  Zalecane narzędzie: **ruff** (`ruff check` + `ruff format`). Formatowanie używa **wcięć tabulatorami**
  (`[tool.ruff.format] indent-style = "tab"`); reguły niekompatybilne z tabami (`W191`, `E101`, `D206`)
  są wyłączone w `pyproject.toml`. Dodaj konfigurację w `pyproject.toml`.
- **Pre-commit** (opcjonalnie, mile widziane): konfiguracja `pre-commit` uruchamiająca lint + format.
- **Brak testów jednostkowych** — nie dodawaj testów jednostkowych; skupiamy się wyłącznie na testach API.

### Struktura repozytorium (proponowana)

```
.
├── .github/
│   └── workflows/
│       └── api-tests.yml          # workflow GitHub Actions
├── fixtures/
│   └── (fixtures pytest)
├── test-data/
│   └── (dane testowe, np. station.json)
├── src/ (lub api/)
│   ├── api_base.py                # klasa ApiBase (ogólne metody CRUD)
│   ├── stations_api.py            # klient Weather Stations API
│   └── weather_api.py             # klient Current Weather API
├── tests/
│   ├── conftest.py                # rejestracja fixtures
│   ├── test_health_checks.py      # health checks usług
│   ├── test_stations_crud.py      # add/update/get/delete stacji
│   └── test_weather.py            # pogoda dla miasta
├── .env.example                   # nazwy zmiennych środowiskowych (bez wartości)
├── .gitignore                     # m.in. .env
├── pyproject.toml                 # konfiguracja ruff/black/pytest
├── requirements.txt               # zależności (lub pyproject)
├── copilot-instructions.md        # instrukcje dla agenta Copilot
└── README.md                      # opis projektu i instrukcja uruchomienia
```

### GitHub Actions — workflow

Przygotuj plik workflow (np. `.github/workflows/api-tests.yml`) gotowy do uruchomienia:

- **wyzwalany na żądanie** (`workflow_dispatch`),
- **przy każdym merge/push do brancha głównego** (`push` do `main`) oraz dla `pull_request` celujących w `main`.

Workflow powinien:
1. Ustawić Pythona (wersja zgodna z projektem, np. 3.11+).
2. Zainstalować zależności.
3. Uruchomić **weryfikację formatowania i lint** (ruff/black — tryb `check`).
4. Uruchomić **testy API** (pytest), korzystając z **sekretów** (`secrets.OPENWEATHER_API_KEY` itd.)
   przekazanych jako zmienne środowiskowe.
5. (Opcjonalnie) opublikować raport z testów jako artefakt.

### Plik `../.github/copilot-instructions.md`

Utwórz plik `../.github/copilot-instructions.md` zawierający co najmniej:
- **Opis projektu** — cel szkoleniowy, zakres (CRUD stacji + pogoda dla miasta), użyty stack.
- **Standard kodowania** — konwencje (AAA, docstringi, nazewnictwo, ruff/black, struktura katalogów,
  zasada „żadnych sekretów w kodzie”, unikalne ID testów).
- **Credentials / Access** — jak skonfigurować dostęp (zmienne środowiskowe, `.env`, `.env.example`,
  GitHub Secrets), gdzie zdobyć klucz API OpenWeatherMap, czego nie commitować.

### Dokumentacja (`README.md`)

`README.md` ma zawierać: opis projektu, wymagania, instrukcję konfiguracji `.env`, sposób uruchomienia
lint/format i testów lokalnie oraz opis działania workflow CI. Odnotuj ewentualne ograniczenia
endpointów (np. wymagany plan subskrypcji) i sposób obsługi w testach (skip).

### Kryteria akceptacji (Definition of Done)

- [ ] Repozytorium publiczne, czytelna struktura jak wyżej.
- [ ] Zaimplementowane testy CRUD stacji (add/update/get/delete) + pogoda dla miasta, w stylu AAA.
- [ ] Każdy test ma jedną asercję, bez instrukcji `if` ani pętli; wiele wartości porównywane przez
      słowniki `expected`/`actual`.
- [ ] Health checks dostępności usług jako niezależne testy (bez bramek `*_service_ready` pomijających
      pozostałe testy).
- [ ] Klasa `ApiBase` z ogólnymi metodami CRUD; klienty dziedziczące po niej.
- [ ] Dane testowe w `test-data/`, fixtures w `fixtures/`.
- [ ] Każda klasa i metoda posiada docstring; nazewnictwo czytelne.
- [ ] Każdy test ma unikalny identyfikator.
- [ ] Konfiguracja (`OPENWEATHER_API_KEY`, `OPENWEATHER_BASE_URL`, `REQUEST_TIMEOUT`) wyłącznie ze
      zmiennych środowiskowych, bez wartości domyślnych; brak którejkolwiek przerywa testy; `.env`
      w `.gitignore`; obecny `.env.example`.
- [ ] Workflow GitHub Actions: `workflow_dispatch` + push/PR do `main`, z lintem/formatem i testami.
- [ ] Mechanizm weryfikacji formatowania (ruff, wcięcia tabulatorami) skonfigurowany i uruchamiany w CI.
- [ ] Plik `../.github/copilot-instructions.md` (opis projektu, standard kodowania, credentials/access).
- [ ] `README.md` z instrukcją uruchomienia.
- [ ] **Brak testów jednostkowych.**
- [ ] Kod prosty, czytelny dla początkujących, łatwy w utrzymaniu i rozbudowie.

### Sposób pracy agenta

1. Najpierw zweryfikuj w dokumentacji endpointy, metody HTTP i wymagania autoryzacji.
2. Przedstaw krótki plan oraz strukturę plików, potem implementuj etapami.
3. Dbaj o to, by testy były niezależne i powtarzalne (setup/teardown danych testowych).
4. Na końcu uruchom lint/format oraz testy i upewnij się, że przechodzą. Gdy brak wymaganych zmiennych
   środowiskowych, testy świadomie się nie uruchamiają (czytelny komunikat konfiguracyjny).
