# Opis pliku: `../.github/workflows/api-tests.yml`

Poniżej znajduje się kopia pliku z komentarzem przy każdej linii, aby łatwo zrozumieć jego rolę w pipeline CI/CD.

```yaml
# [1] name: API tests
# Definiuje nazwę workflow, która będzie widoczna w GitHub Actions.
name: API tests

# [2] on:
# Ustawia eventy, które uruchamiają workflow.
on:
  # [3] workflow_dispatch:
  # Pozwala ręcznie uruchomić pipeline z poziomu interfejsu GitHub.
  workflow_dispatch:

  # [4] push:
  # Uruchamia workflow po wysłaniu zmian do gałęzi main.
  push:
    # [5] branches: [main]
    # Ogranicza uruchomienie do gałęzi main.
    branches: [main]

  # [6] pull_request:
  # Uruchamia workflow dla pull requestów kierowanych do main.
  pull_request:
    # [7] branches: [main]
    # Dotyczy tylko PR-ów bazujących na gałęzi main.
    branches: [main]

# [8] permissions:
# Ustawia minimalne uprawnienia wymagane do odczytu treści repozytorium.
permissions:
  # [9] contents: read
  # Pozwala tylko na odczyt zawartości repozytorium.
  contents: read

# [10] concurrency:
# Zapobiega równoległemu uruchamianiu wielu kopii workflow dla tego samego referencji.
concurrency:
  # [11] group: api-tests-${{ github.ref }}
  # Klucz grupy kolejki; pozwala odróżniać uruchomienia dla różnych branchy / refs.
  group: api-tests-${{ github.ref }}
  # [12] cancel-in-progress: true
  # Jeśli pojawi się nowe uruchomienie, poprzednie zostanie anulowane.
  cancel-in-progress: true

# [13] jobs:
# Definiuje listę zadań (jobów), które mają zostać wykonane.
jobs:
  # [14] lint:
  # Job odpowiedzialny za sprawdzenie jakości kodu i formatowania.
  lint:
    # [15] name: Lint & format check
    # Nazwa jobu widoczna w GitHub Actions.
    name: Lint & format check
    # [16] runs-on: ubuntu-latest
    # Uruchamia job na najnowszym obrazie Ubuntu w GitHub-hosted runnerze.
    runs-on: ubuntu-latest
    # [17] steps:
    # Lista kroków jobu, wykonywanych sekwencyjnie.
    steps:
      # [18] - name: Checkout
      # Pobiera kod źródłowy repozytorium do środowiska uruchomieniowego.
      - name: Checkout
        # [19] uses: actions/checkout@v7
        # Używa oficjalnej akcji do pobrania repozytorium.
        uses: actions/checkout@v7

      # [20] - name: Set up Python
      # Konfiguruje środowisko Pythona do uruchamiania testów i lintów.
      - name: Set up Python
        # [21] uses: actions/setup-python@v7
        # Instaluje i konfiguruje wskazaną wersję Python.
        uses: actions/setup-python@v7
        # [22] with:
        # Parametry przekazywane do akcji setup-python.
        with:
          # [23] python-version: "3.12"
          # Ustawia wersję interpretera na Python 3.12.
          python-version: "3.12"
          # [24] cache: pip
          # Włącza cache dla zależności Pythona, aby przyspieszyć kolejne uruchomienia.
          cache: pip

      # [25] - name: Install dependencies
      # Instaluje wszystkie wymagane biblioteki z pliku requirements.txt.
      - name: Install dependencies
        # [26] run: pip install -r requirements.txt
        # Instaluje zależności projektu.
        run: pip install -r requirements.txt

      # [27] - name: Ruff lint
      # Uruchamia analizę statyczną Ruff z konfiguracją GitHub annotations.
      - name: Ruff lint
        # [28] run: ruff check --output-format=github .
        # Wykonuje sprawdzenie lintu i formatuje wynik w formacie kompatybilnym z GitHub.
        run: ruff check --output-format=github .

      # [29] - name: Ruff format check
      # Sprawdza, czy kod jest sformatowany zgodnie z regułami Ruff.
      - name: Ruff format check
        # [30] run: ruff format --check --diff .
        # Weryfikuje format plików i pokazuje różnice bez automatycznego formatowania.
        run: ruff format --check --diff .

  # [31] api-tests:
  # Job przeznaczony do uruchamiania testów API po pomyślnym wykonaniu lintu.
  api-tests:
    # [32] name: API tests
    # Wyświetlana nazwa jobu w UI GitHub Actions.
    name: API tests
    # [33] needs: lint
    # Ustawia zależność: ten job uruchomi się dopiero po zakończeniu jobu lint.
    needs: lint
    # [34] runs-on: ubuntu-latest
    # Testy API są uruchamiane na najnowszym Ubuntu.
    runs-on: ubuntu-latest
    # [35] env:
    # Definiuje zmienne środowiskowe dostępne w jobie.
    env:
      # [36] OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
      # Pobiera klucz API z tajnych zmiennych repozytorium.
      OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
      # [37] OPENWEATHER_BASE_URL: ${{ vars.OPENWEATHER_BASE_URL || 'https://api.openweathermap.org' }}
      # Ustawia bazowy URL usługi OpenWeatherMap, z fallbackiem do publicznego endpointu.
      OPENWEATHER_BASE_URL: ${{ vars.OPENWEATHER_BASE_URL || 'https://api.openweathermap.org' }}
      # [38] REQUEST_TIMEOUT: ${{ vars.REQUEST_TIMEOUT || '10' }}
      # Ustawia timeout zapytań w sekundach, z wartością domyślną 10.
      REQUEST_TIMEOUT: ${{ vars.REQUEST_TIMEOUT || '10' }}
    # [39] steps:
    # Lista kroków wykonywanych w jobie testów API.
    steps:
      # [40] - name: Checkout
      # Pobiera kod źródłowy przed uruchomieniem testów.
      - name: Checkout
        # [41] uses: actions/checkout@v7
        # Ponownie używa akcji checkout do pobrania repozytorium.
        uses: actions/checkout@v7

      # [42] - name: Set up Python
      # Konfiguruje środowisko testowe Pythona.
      - name: Set up Python
        # [43] uses: actions/setup-python@v7
        # Instalacja i konfiguracja Pythona 3.12.
        uses: actions/setup-python@v7
        # [44] with:
        # Parametry przekazywane do setup-python.
        with:
          # [45] python-version: "3.12"
          # Ustawia wersję interpretera zgodną z wymaganiami projektu.
          python-version: "3.12"
          # [46] cache: pip
          # Przyspiesza instalację zależności poprzez cache pip.
          cache: pip

      # [47] - name: Install dependencies
      # Instaluje biblioteki używane przez testy i aplikację.
      - name: Install dependencies
        # [48] run: pip install -r requirements.txt
        # Instalacja zależności z pliku requirements.txt.
        run: pip install -r requirements.txt

      # [49] - name: Warn when API key secret is missing
      # Wyświetla ostrzeżenie, jeśli klucz API nie został ustawiony w sekretnych zmiennych.
      - name: Warn when API key secret is missing
        # [50] if: env.OPENWEATHER_API_KEY == ''
        # Wykonuje ten krok tylko wtedy, gdy secret z kluczem API jest pusty.
        if: env.OPENWEATHER_API_KEY == ''
        # [51] run: >
        # Używa multi-line string, aby wygodnie zbudować komunikat ostrzeżenia.
        run: >
          # [52] echo "::warning title=Missing secret::OPENWEATHER_API_KEY is not set
          # Wypisuje ostrzeżenie do GitHub Actions, że klucz nie jest ustawiony.
          echo "::warning title=Missing secret::OPENWEATHER_API_KEY is not set
          # [53] (e.g. pull requests from forks) - API tests will be skipped."
          # Kontynuuje tekst ostrzeżenia, informując, że testy zostaną pominięte.
          (e.g. pull requests from forks) - API tests will be skipped."

      # [54] - name: Run API tests
      # Uruchamia testy automatyczne tylko wtedy, gdy klucz API jest dostępny.
      - name: Run API tests
        # [55] if: env.OPENWEATHER_API_KEY != ''
        # Kontroluje wykonanie kroku tylko przy obecności klucza API.
        if: env.OPENWEATHER_API_KEY != ''
        # [56] run: >
        # Umożliwia zapis poleceń testowych w formie wielowierszowej.
        run: >
          # [57] pytest
          # Wykonuje testy pytest.
          pytest
          # [58] --junitxml=reports/junit.xml
          # Zapisuje wynik w formacie JUnit do katalogu reports.
          --junitxml=reports/junit.xml
          # [59] --html=reports/report.html --self-contained-html
          # Generuje HTML report z wynikami testów oraz osadza potrzebne zasoby w jednym pliku.
          --html=reports/report.html --self-contained-html

      # [60] - name: Upload test report
      # Zapisuje raport testowy jako artefakt w GitHub Actions, nawet jeśli testy się nie powiodły.
      - name: Upload test report
        # [61] if: always()
        # Wykonuje krok niezależnie od wyniku poprzednich etapów.
        if: always()
        # [62] uses: actions/upload-artifact@v7
        # Publikuje wygenerowane pliki raportów jako artefakt CI.
        uses: actions/upload-artifact@v7
        # [63] with:
        # Parametry akcji upload-artifact.
        with:
          # [64] name: api-test-report
          # Nazwa artefaktu widoczna w GitHub Actions.
          name: api-test-report
          # [65] path: reports/
          # Ładuje wszystkie pliki z katalogu reports jako artefakt.
          path: reports/
          # [66] if-no-files-found: ignore
          # Jeśli brak plików raportu, nie powoduje błędu wykonania.
          if-no-files-found: ignore
```

## Krótki opis działania workflow

Ten plik definiuje automatyczną integrację ciągłą dla projektu API. Workflow wykonuje następujące etapy:

1. Po każdym pushu lub pull request do `main` uruchamia się pipeline.
2. Najpierw wykonuje się job `lint`, który sprawdza:
   - poprawność zależności,
   - zgodność z regułami Ruff,
   - formatowanie kodu.
3. Po pomyślnym zakończeniu lintu uruchamia się job `api-tests`.
4. Job `api-tests`:
   - pobiera kod,
   - ustawia Pythona,
   - instaluje zależności,
   - sprawdza, czy klucz API został ustawiony,
   - uruchamia testy `pytest` z raportami JUnit i HTML,
   - zapisuje raport jako artefakt nawet w przypadku błędu.

Cel tego workflow to automatyczna walidacja jakości i poprawności testów API przed scaleniem zmian do main.
