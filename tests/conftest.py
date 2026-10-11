"""Konfiguracja pytest: rejestracja fixtures oraz obsługa unikalnych identyfikatorów testów.

Każdy test musi mieć marker `@pytest.mark.test_id("TC-XXX-NNN")`. Identyfikator:
    * jest weryfikowany pod kątem obecności i unikalności podczas zbierania testów,
    * pozwala uruchomić test poleceniem `pytest -k TC-STA-001`,
    * trafia do logów, raportu JUnit XML (`<property name="test_id">`) i raportu HTML.
"""

import logging

import pytest

from utils.config import MissingEnvironmentError, Settings

pytest_plugins = [
	"fixtures.config_fixtures",
	"fixtures.client_fixtures",
	"fixtures.health_fixtures",
	"fixtures.station_fixtures",
	"fixtures.weather_fixtures",
]

TEST_ID_MARKER = "test_id"
TEST_ID_PROPERTY = "test_id"

logger = logging.getLogger(__name__)


def get_test_id(item: pytest.Item) -> str | None:
	"""Zwraca identyfikator testu z markera `test_id`.

	Args:
		item: Zebrany test pytest.

	Returns:
		Identyfikator testu lub None, gdy marker nie został ustawiony.
	"""
	marker = item.get_closest_marker(TEST_ID_MARKER)
	return str(marker.args[0]) if marker and marker.args else None


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
	"""Weryfikuje, że każdy test ma unikalny identyfikator i udostępnia go w raportach.

	Args:
		config: Konfiguracja pytest.
		items: Lista zebranych testów.

	Raises:
		pytest.UsageError: Gdy test nie ma identyfikatora lub identyfikator się powtarza.
	"""
	owners: dict[str, str] = {}
	errors: list[str] = []

	for item in items:
		test_id = get_test_id(item)
		if test_id is None:
			errors.append(f"{item.nodeid}: brak markera @pytest.mark.{TEST_ID_MARKER}('...')")
			continue
		if test_id in owners:
			errors.append(f"{item.nodeid}: identyfikator {test_id} użyty już w {owners[test_id]}")
			continue

		owners[test_id] = item.nodeid
		item.user_properties.append((TEST_ID_PROPERTY, test_id))
		item.extra_keyword_matches.add(test_id)

	if errors:
		raise pytest.UsageError("Niepoprawne identyfikatory testów:\n" + "\n".join(errors))


def pytest_runtest_setup(item: pytest.Item) -> None:
	"""Loguje identyfikator testu na początku jego wykonania.

	Args:
		item: Uruchamiany test.
	"""
	logger.info("[%s] START %s", get_test_id(item), item.nodeid)


def pytest_configure(config: pytest.Config) -> None:
	"""Weryfikuje konfigurację środowiska i rejestruje kolumnę "Test ID" w raporcie HTML.

	Przerywa całą sesję testową, gdy którakolwiek wymagana zmienna środowiskowa nie
	została ustawiona, aby nie uruchamiać testów bez pełnej konfiguracji.

	Args:
		config: Konfiguracja pytest.

	Raises:
		pytest.UsageError: Gdy brakuje wymaganych zmiennych środowiskowych.
	"""
	try:
		Settings.from_env()
	except MissingEnvironmentError as error:
		raise pytest.UsageError(str(error)) from error

	if config.pluginmanager.hasplugin("html"):
		config.pluginmanager.register(HtmlTestIdColumn(), "html-test-id-column")


class HtmlTestIdColumn:
	"""Plugin dodający kolumnę "Test ID" do raportu pytest-html."""

	@staticmethod
	def pytest_html_results_table_header(cells: list[str]) -> None:
		"""Dodaje nagłówek kolumny "Test ID".

		Args:
			cells: Komórki nagłówka tabeli wyników.
		"""
		cells.insert(1, "<th>Test ID</th>")

	@staticmethod
	def pytest_html_results_table_row(report: pytest.TestReport, cells: list[str]) -> None:
		"""Dodaje identyfikator testu w wierszu tabeli wyników.

		Args:
			report: Raport z wykonania testu.
			cells: Komórki wiersza tabeli wyników.
		"""
		test_id = dict(report.user_properties).get(TEST_ID_PROPERTY, "")
		cells.insert(1, f"<td>{test_id}</td>")
