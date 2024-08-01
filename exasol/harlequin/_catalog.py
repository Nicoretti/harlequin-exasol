from contextlib import closing
from harlequin.catalog import CatalogItem
from itertools import chain


class Catalog:
    def __init__(self, connection):
        self._connection = connection

    @property
    def items(self):
        items = []
        user = CatalogItem(
            qualified_identifier="/User",
            query_name="",
            label="Schemas",
            type_label="S",
            children=self._schemas(),
        )

        system = CatalogItem(
            qualified_identifier="/SYS",
            query_name="",
            label="System Tables",
            type_label="SYS",
            children=self._system_tables(),
        )

        items.append(system)
        items.append(user)

        catalog = [
            CatalogItem(
                qualified_identifier="/",
                query_name="",
                label="Database",
                type_label="DB",
                children=items,
            )
        ]
        return catalog

    def _list(self, query):
        with closing(self._connection.cursor()) as cursor:
            cursor.execute(query)
            items = (name for (name,) in cursor.fetchall())
            return list(items)

    def _system_tables(self):
        with closing(self._connection.cursor()) as cursor:
            query = "SELECT OBJECT_NAME, OBJECT_TYPE, SCHEMA_NAME FROM EXA_SYSCAT;"
            cursor.execute(query)
            relations = cursor.fetchall()
            relations = list(relations)

        # TODO: consider create subtrees for schemas sys, exas_statistics ...
        items = [
            CatalogItem(
                qualified_identifier=f'"{o_schema}"."{o_name}"',
                query_name=f'"{o_schema}"."{o_name}"',
                label=o_name,
                type_label="t" if o_type.upper() == "TABLE" else "v",
                # QUESTION: where to find definition of system tables?
                # children=self._columns(o_schema, o_name),
            )
            for o_name, o_type, o_schema in relations
        ]
        return items

    def _schemas(self):
        query = "SELECT SCHEMA_NAME FROM EXA_ALL_SCHEMAS;"
        schemas = self._list(query)
        items = [
            CatalogItem(
                qualified_identifier=schema,
                query_name=schema,
                label=schema,
                type_label="s",
                children=self._tables(schema),
            )
            for schema in schemas
        ]
        return items

    def _relations(self, schema):
        tables = self._tables(schema)
        views = self._views(schema)
        relations = sorted(chain(tables, views))
        return relations

    def _views(self, schema):
        # Prepared statement of the DB-API 2 layer seems to have issues in the
        # WHERE clause if string escape/conversion is required
        query = f"SELECT VIEW_NAME FROM EXA_ALL_VIEWS WHERE VIEW_SCHEMA='{schema}';"
        views = self._list(query)
        items = [
            CatalogItem(
                qualified_identifier=f'"{schema}"."{view}"',
                query_name=f'"{schema}"."{view}"',
                label=view,
                type_label="v",
                children=self._columns(schema, view),
            )
            for view in views
        ]
        return items

    def _tables(self, schema):
        # Prepared statement of the DB-API 2 layer seems to have issues in the
        # WHERE clause if string escape/conversion is required
        query = f"SELECT TABLE_NAME FROM EXA_ALL_TABLES WHERE TABLE_SCHEMA='{schema}';"
        tables = self._list(query)
        items = [
            CatalogItem(
                qualified_identifier=f'"{schema}"."{table}"',
                query_name=f'"{schema}"."{table}"',
                label=table,
                type_label="t",
                children=self._columns(schema, table),
            )
            for table in tables
        ]
        return items

    def _columns(self, schema, relation):
        with closing(self._connection.cursor()) as cursor:
            # Prepared statement of the DB-API 2 layer seems to have issues in the
            # WHERE clause if string escape/conversion is required
            query = (
                "SELECT COLUMN_NAME, COLUMN_TYPE FROM EXA_ALL_COLUMNS "
                f"WHERE COLUMN_SCHEMA='{schema}' and COLUMN_TABLE='{relation}';"
            )
            cursor.execute(query)
            columns = cursor.fetchall()
            columns = list(columns)

        items = [
            CatalogItem(
                qualified_identifier=f'"{schema}"."{relation}"."{column_name}"',
                query_name=f'"{schema}"."{relation}"."{column_name}"',
                label=f"{column_name}",
                type_label=f"{column_type}",
            )
            for column_name, column_type in columns
        ]
        return items
