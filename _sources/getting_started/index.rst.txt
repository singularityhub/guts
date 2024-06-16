.. _getting-started:

===============
Getting Started
===============

Guts is a small library to help expose contents of containers. For this
first draft, we:

1. Find PATH variables from the container configs
2. Statically parse the exported filesystem to discover executables there.

And since we want to find "special" executables in a container, the intended
workflow will be to have a set of core bases (e.g., ubuntu) that we can subtract
one.
If you have any questions or issues, please `let us know <https://github.com/singularityhub/guts/issues>`_

.. toctree::
   :maxdepth: 2

   installation
   user-guide
