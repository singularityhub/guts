.. _getting_started-installation:

============
Installation
============

Guts can be installed from pypi, or from source. You'll need docker installed.

Pypi
====

If you want to use Guts locally on your machine or via some custom install,
the module is available in pypi as `the pakages project <https://pypi.org/project/container-guts/>`_.

.. code:: console

    $ pip install container-guts

This will provide the latest release. If you want a branch or development version, you can install from GitHub, shown next.

Virtual Environment
===================

Here is how to clone the repository and do a local install.

.. code:: console

    $ git clone https://github.com/singularityhub/guts
    $ cd guts

Create a virtual environment (recommended)

.. code:: console

    $ python -m venv env
    $ source env/bin/activate


And then install (this is development mode, remove the -e to not use it)

.. code:: console

    $ pip install -e .

Installation of pakages adds an executable, ``pakages`` to your path.

.. code:: console

    $ which guts
    /opt/conda/bin/guts


Once it's installed, you should be able to inspect the client!

.. code-block:: console

    $ guts --help


You'll next want to install or build packages, discussed in :ref:`getting-started`.
