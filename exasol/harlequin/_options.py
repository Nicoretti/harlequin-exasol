from __future__ import annotations

from harlequin.options import (
    FlagOption,
    TextOption,
)


def _int_validator(s: str | None) -> tuple[bool, str]:
    if s is None:
        return True, ""
    try:
        _ = int(s)
    except ValueError:
        return False, f"Cannot convert {s} to an int!"
    else:
        return True, ""


host = TextOption(
    name="host",
    description=("The host name or IP address of the Exasol server."),
    short_decls=["-h"],
    default="localhost",
)


port = TextOption(
    name="port",
    description=("The TCP/IP port of the Exasol server. Must be an integer."),
    short_decls=["-p"],
    default="8563",
    validator=_int_validator,
)


database = TextOption(
    name="schema",
    description=(
        "The schema name to open when connecting to the Exasol server."),
    short_decls=["-s"],
    default="",
)


user = TextOption(
    name="user",
    description=("The user name used to authenticate with the Exasol server."),
    short_decls=["-u", "--username"],
    default="sys",
)


password = TextOption(
    name="password",
    description=(
        "The password to authenticate the user with the Exasol server."),
    default="exasol",
)


tls = FlagOption(
    name="unsecure", description="Disable transport layer security.", default="False"
)

certificate_validation = FlagOption(
    name="disable-certificate-validation",
    description="Disable certificate validation connecting to server using tls.",
    default="False",
)


OPTIONS = [
    host,
    port,
    database,
    user,
    password,
    tls,
    certificate_validation,
]
