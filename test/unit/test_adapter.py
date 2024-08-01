import sys
import pytest

from typing import Generator

from exasol.harlequin import Exasol, Connection
from harlequin import HarlequinAdapter, HarlequinConnection, HarlequinCursor
from harlequin.exception import HarlequinQueryError
from harlequin.catalog import Catalog, CatalogItem


if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from textual_fastdatatable.backend import create_backend


@pytest.fixture
def plugin():
    return "exasol"


@pytest.fixture
def harlequin_entry_points():
    eps = entry_points(group="harlequin.adapter")
    yield eps


@pytest.fixture
def connection() -> Generator[Connection, None, None]:
    con = Connection(unsecure=True)
    con.connect()
    yield con
    con.close()


def test_plugin_discovery(plugin) -> None:
    eps = entry_points(group="harlequin.adapter")
    assert eps[plugin]


def test_load_plugin(plugin, harlequin_entry_points) -> None:
    adapter_cls = harlequin_entry_points[plugin].load()
    assert adapter_cls == Exasol
    assert issubclass(adapter_cls, HarlequinAdapter)


def test_connect():
    adapter = Exasol(unsecure=True)
    expected = HarlequinConnection
    actual = adapter.connect()
    assert isinstance(actual, expected)


@pytest.mark.xfail(reason="Not Implemented Yet")
def test_kwargs():
    assert False


@pytest.mark.xfail(reason="Not Implemented Yet")
def test_connection_error():
    assert False


def test_get_catalog(connection) -> None:
    catalog = connection.get_catalog()
    assert isinstance(catalog, Catalog)
    assert catalog.items
    assert isinstance(catalog.items[0], CatalogItem)


@pytest.mark.xfail(reason="Not Implemented Yet")
def test_get_completions(connection) -> None:
    completions = connection.get_completions()
    test_labels = ["atomic", "greatest", "point_right", "autovacuum"]
    filtered = list(filter(lambda x: x.label in test_labels, completions))
    assert len(filtered) == 4
    value_filtered = list(
        filter(lambda x: x.value in test_labels, completions))
    assert len(value_filtered) == 4


def test_execute_ddl(connection) -> None:
    cur = connection.execute("create table foo (a int)")
    assert cur is None


def test_execute_select(connection) -> None:
    cur = connection.execute("select 1 as a")
    assert isinstance(cur, HarlequinCursor)
    assert cur.columns() == [("A", "Decimal")]
    data = cur.fetchall()
    backend = create_backend(data)
    assert backend.column_count == 1
    assert backend.row_count == 1


@pytest.mark.xfail(reason="Not Implemented Yet")
def test_execute_select_dupe_cols(connection) -> None:
    cur = connection.execute("select 1 as a, 2 as a, 3 as a")
    assert isinstance(cur, HarlequinCursor)
    assert len(cur.columns()) == 3
    data = cur.fetchall()
    backend = create_backend(data)
    assert backend.column_count == 3
    assert backend.row_count == 1


def test_set_limit(connection) -> None:
    cur = connection.execute(
        "select 1 as a union all select 2 union all select 3")
    assert isinstance(cur, HarlequinCursor)
    cur = cur.set_limit(2)
    assert isinstance(cur, HarlequinCursor)
    data = cur.fetchall()
    backend = create_backend(data)
    assert backend.column_count == 1
    assert backend.row_count == 2


def test_execute_raises_query_error(connection) -> None:
    with pytest.raises(HarlequinQueryError):
        _ = connection.execute("sel;")
