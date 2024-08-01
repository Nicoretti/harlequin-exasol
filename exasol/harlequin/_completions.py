from __future__ import annotations

from typing import List
from inspect import cleandoc
from harlequin import HarlequinCompletion
from functools import cache
from contextlib import closing


class Completions:
    def __init__(self, connection):
        self._connection = connection

    @property
    def all(self) -> List[HarlequinCompletion]:
        completions = self._keywords()
        return list(completions)

    @cache
    def _keywords(self) -> List[HarlequinCompletion]:
        query = cleandoc(
            """
            SELECT DISTINCT keyword, reserved
            FROM EXA_SQL_KEYWORDS
            WHERE reserved IS TRUE
            ORDER BY keyword;
            """
        )
        with closing(self._connection.cursor()) as cursor:
            cursor.execute(query)
            keywords = cursor.fetchall()

        completions = [
            HarlequinCompletion(
                label=keyword,
                type_label="kw",
                value=keyword,
                priority=100 if is_reserved else 1000,
                context=None,
            )
            for (keyword, is_reserved) in keywords
        ]
        return completions
