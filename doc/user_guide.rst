.. _user_guide:

:octicon:`person` User Guide
============================

Getting Started
+++++++++++++++

Install the package using `pipx`:

.. code-block:: shell

    pipx install harlequin-exasol

Open Harlequin and connect it to your database:

.. code-block:: shell

    harlequin -a exasol --schema 'foo' --host '8.9.10.1' --port 8563 ...

.. note::

    For further help on the supported settings and flags, check out the `exasol Adapter Options` section in the help provided by harlequin :code:`harlequin --help`.


Details about Harlequin can be found on the `official website <https://harlequin.sh>`_

* `Keyboard bindings <https://harlequin.sh/docs/bindings>`_
* `Configuration <https://harlequin.sh/docs/config-file>`_
* `Theming <https://harlequin.sh/docs/themes>`_
