.. _manual-main:

===============
Container Guts!
===============

.. image:: https://img.shields.io/github/stars/singularityhub/guts?style=social
    :alt: GitHub stars
    :target: https://github.com/singularityhub/guts/stargazers


Guts is a small library to help expose contents of containers. For this
first draft, we:

1. Find PATH variables from the container configs
2. Statically parse the exported filesystem to discover executables there.

And since we want to find "special" executables in a container, the intended
workflow will be to have a set of core bases (e.g., ubuntu) that we can subtract
one. The additions are what are left after that.
We currently support the following container technologies:

 - `Docker <https://www.docker.com/>`_

To see the code, head over to the `repository <https://github.com/singularityhub/guts/>`_.


.. _main-getting-started:

-----------------------------------
Getting started with Container Guts
-----------------------------------

Container Guts "Guts" can be installed from pypi or directly from the repository. See :ref:`getting_started-installation` for
installation, and then the :ref:`getting-started` section for using the client.

.. _main-support:

-------
Support
-------

* For **bugs and feature requests**, please use the `issue tracker <https://github.com/singularityhub/guts/issues>`_.
* For **contributions**, visit Caliper on `Github <https://github.com/singularityhub/guts>`_.

---------
Resources
---------

`GitHub Repository <https://github.com/singularityhub/guts>`_
    The code for Guts on GitHub.

.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 2

   getting_started/index
   getting_started/user-guide

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 2

    api_reference/container_guts
    api_reference/modules
