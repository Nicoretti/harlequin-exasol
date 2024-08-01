from __future__ import annotations
from exasol.driver.websocket import dbapi2
from exasol.harlequin._options import OPTIONS
from exasol.harlequin._completions import Completions
from harlequin import catalog
from exasol.harlequin._catalog import Catalog
from typing import Any, Sequence

from pathlib import Path

from harlequin import (
    HarlequinAdapter,
    HarlequinConnection,
    HarlequinTransactionMode,
    HarlequinCursor,
    HarlequinCompletion,
)
from harlequin.exception import HarlequinQueryError
from textual_fastdatatable.backend import AutoBackendType


class Cursor(HarlequinCursor):
    def __init__(self, conn: Connection, cur: dbapi2.Cursor) -> None:
        self.conn = conn
        self.cur = cur
        self._limit: int | None = None

    def columns(self) -> list[tuple[str, str]]:
        assert self.cur.description is not None

        def describe(column_description):
            name, typename = (column_description[0], column_description[1].name)
            return name, typename

        return [describe(col_desc) for col_desc in self.cur.description]

    def set_limit(self, limit: int) -> Cursor:
        self._limit = limit
        return self

    def fetchall(self) -> AutoBackendType:
        try:
            if self._limit is None:
                return self.cur.fetchall()
            else:
                return self.cur.fetchmany(self._limit)
        except Exception as e:
            raise HarlequinQueryError(
                msg=str(e),
                title="Harlequin encountered an error while executing your query.",
            ) from e


class Connection(HarlequinConnection):
    def __init__(self, *args: Any, init_message: str = "", **kwargs: Any) -> None:
        """
        Args:
            init_message (str): If set, Harlequin will notify the user with the
            message after the connection is created.
        """
        self.init_message = init_message
        settings = {
            "dsn": f'{kwargs.get("host", "127.0.0.1")}:{kwargs.get("port", 8563)}',
            "username": kwargs.get("user", "sys"),
            "password": kwargs.get("password", "exasol"),
            "schema": kwargs.get("schema", ""),
            "tls": not kwargs.get("unsecure", False),
            "certificate_validation": not kwargs.get(
                "disable_certificate_validation", False
            ),
        }

        self._supported_kwargs = {
            "dsn",
            "username",
            "password",
            "schema",
            "autocommit",
            "tls",
            "certificate_validation",
        }
        self._kwargs = {
            key: value
            for key, value in settings.items()
            if key in self._supported_kwargs
        }
        self._connection = None

    def connect(self, **kwargs) -> "Connection":
        filtered_kwargs = {
            key: value for key, value in kwargs.items() if key in self._supported_kwargs
        }
        self._kwargs.update(filtered_kwargs)
        self._connection = dbapi2.connect(**self._kwargs)
        self._completions = Completions(self._connection)
        self._catalog = Catalog(self._connection)

    def execute(self, query: str) -> HarlequinCursor | None:
        """
        Executes query and returns a cursor (for a select stmt) or None. Raises
        HarlequinQueryError if the database raises an error in response to the query.

        Args:
            query (str): The text of a single query to execute

        Returns: HarlequinCursor | None

        Raises: HarlequinQueryError
        """
        cursor = self._connection.cursor()
        try:
            cursor.execute(query)
        except Exception as ex:
            cursor.close()
            raise HarlequinQueryError(
                msg=str(ex),
                title="Harlequin encountered an error while executing your query.",
            ) from ex

        if cursor.description is None:
            cursor.close()
            return None

        return Cursor(self, cursor)

    def get_catalog(self) -> Catalog:
        """
        Introspects the connected database and returns a Catalog object with
        items for each database, schema, table, view, column, etc.

        Returns: Catalog
        """
        return catalog.Catalog(items=self._catalog.items)

    def get_completions(self) -> list[HarlequinCompletion]:
        """
        Returns a list of extra completions to make available to the Query Editor's
        autocomplete. These could be dialect-specific functions, keywords, etc.
        Harlequin ships with a basic list of common ANSI-SQL keywords and functions.

        It is not necessary to provide completions for Catalog items, since Harlequin
        will create those from the Catalog.

        Returns: list[HarlequinCompletion]
        """
        return self._completions.all

    def copy(
        self, query: str, path: Path, format_name: str, options: dict[str, Any]
    ) -> None:
        """
        Exports data returned by query to a file or directory at path, using
        options.
        Args:
            query (str): The text of the query (select stmt) to be executed.
            path (Path): The destination location for the file(s) to be written.
            format_name (str): The name of the selected export format.
            options (dict[str, Any]): A dict of format option names and values.

        Returns: None

        Raises:
            NotImplementedError if the adapter does not have copy functionality.
            HarlequinCopyError for all other exceptions during export.
        """
        raise NotImplementedError

    def validate_sql(self, text: str) -> str:
        """
        Parses text as one or more queries; returns text if parsing does not result
        in an error; otherwise returns the empty string ("").

        Args:
            text (str): The text, which may compose one or more queries and partial
                queries.

        Returns: str, either the original text or the empty string ("")

        Raises: NotImplementedError if the adapter does not provide this optional
            functionality.
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        Closes the connection, if necessary. This function is called when the app
        quits.

        Returns: None
        """
        if not self._connection:
            self._connection.close()

    @property
    def transaction_mode(self) -> HarlequinTransactionMode | None:
        """
        The user-facing label of the currently-active transaction mode.

        Returns None if the adapter does not support different
        transaction modes.

        Returns: HarlequinTransactionMode | None
        """
        return None

    def toggle_transaction_mode(self) -> HarlequinTransactionMode | None:
        """
        Switches to the next transaction mode in the adapter's sequence of modes
        and returns the new mode.

        No-ops and returns None if the adapter does not support different
        transaction modes.

        Returns: HarlequinTransactionMode, the new mode, after toggling, or None.
        """
        return None


class Exasol(HarlequinAdapter):
    ADAPTER_OPTIONS = OPTIONS

    def __init__(self, conn_str: Sequence[str] = "", **options: Any) -> None:
        """
        Initialize an adapter.

        Args:
            - conn_str (Sequence[str]): One or more connection strings. May be empty.
            - **options (Any): Options received from the command line, config file,
                or env variables. Adapters should be robust to receiving both subsets
                and supersets of their declared options. They should disregard any
                extra (unexpected) kwargs. Adapters should check the types of options,
                as they may not be cast to the correct types.

        Raises: HarlequinConfigError if a received option is the wrong value or type.
        """
        self._options = dict()
        if conn_str:
            self._options["dsn"] = conn_str
        self._options.update(options)

    def connect(self) -> HarlequinConnection:
        con = Connection(**self._options)
        con.connect()
        return con
