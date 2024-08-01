<h1 align="center">harlequin-exasol</h1>

<p align="center">
Harelequin adapter for Exasol
</p>

<p align="center">

<a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/pypi/l/harlequin-exasol" alt="License">
</a>
<a href="https://pypi.org/project/harlequin-exasol/">
    <img src="https://img.shields.io/pypi/dm/harlequin-exasol" alt="Downloads">
</a>
<a href="https://pypi.org/project/harlequin-exasol/">
    <img src="https://img.shields.io/pypi/pyversions/harlequin-exasol" alt="Supported Python Versions">
</a>
<a href="https://pypi.org/project/harlequin-exasol/">
    <img src="https://img.shields.io/pypi/v/harlequin-exasol" alt="PyPi Package">
</a>
</p>


## ⚠️ Disclaimer

**The current state of this project is a spike—an initial evaluation of what is possible and how much effort specific tasks will require. It should only be used for evaluating Exasol usage via Harlequin.**

**Below, you will find information if you are interested in trying it out and getting an idea of it. While issues reported beyond the mentioned limitations are welcome for tracking purposes, addressing these issues is unlikely at any point. However, having a list of issues may be helpful to other evaluators.**

## 🚀 Features

* Basic Catalog
* Basic Query Completion
* Basic Query Support, including DDL

## Getting Started

### 🔌️ Prerequisites

- [Python](https://www.python.org/) >= 3.9

### 💾 Installation

Install the package using `pipx`:

```shell
pipx install harlequin-exasol --include-deps
```

### ▶️ Starting Harlequin

Open Harlequin and connect it to your database:

```shell
harlequin -a exasol --schema 'foo' --host '8.9.10.1' --port 8563 ...
```

For connecting to a standard [Exasol Docker DB](https://hub.docker.com/r/exasol/docker-db/), most defaults should work just fine:

```shell
harlequin -a exasol --disable-certificate-validation
```

## 📚 Documentation

> **Note:**
> For further help on the supported settings and flags, check out the `Exasol Adapter Options` section in the help provided by Harlequin:
>
> ```shell
> harlequin --help
> ```

Details about Harlequin can be found on the [official website](https://harlequin.sh):

- [Keyboard bindings](https://harlequin.sh/docs/bindings)
- [Configuration](https://harlequin.sh/docs/config-file)
- [Theming](https://harlequin.sh/docs/themes)

## 📝 Todo's

* Investigate dbapi2 issue with parameters in the prepared statement where clause (`exasol.driver.dbapi2`):

    ```python
    schema = 'foo'
    query = f"SELECT TABLE_NAME FROM EXA_ALL_TABLES WHERE TABLE_SCHEMA='{schema}';"
    cursor.execute(query)
    ```

    vs

    ```python
    schema = 'foo'
    query = "SELECT TABLE_NAME FROM EXA_ALL_TABLES WHERE TABLE_SCHEMA=?;"
    cursor.execute(query, schema)
    ```

* Consider making catalog functions asynchronous to improve progress indicator updates.
* Support subcategories for system tables based on schema (`SYS`, `EXA_STATISTICS`).
* Support table details (columns) for system tables.
* Add/Update unit/integration tests.
* Add CI/CD.
* Contact the maintainer of Harlequin to mention Exasol support on the [Harlequin website](https://harlequin.sh).
