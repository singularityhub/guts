.. _getting_started-user-guide:

==========
User Guide
==========


If you haven't installed Guts yet, you should read :ref:`getting_started-installation` first.

Commands
========

Guts currently has just one client command, "manifest" to
get a manifest of executables on the ``PATH``!

--------
Manifest
--------

Using guts on the command line is the easiest way to test it manually,
and by default, the results will be printed to the screen. The manifest
command will generate "guts" for an image:

.. code-block:: console

    $ guts manifest ubuntu

If you provide an output file, it will save to it:

.. code-block:: console

    $ guts manifest --outfile ubuntu-guts.json ubuntu

By default, we extract executables on the PATH. However, you can also ask
to extract all filesystem paths:

.. code-block:: console

    $ guts manifest --include fs ubuntu


Or to get fs and paths:

.. code-block:: console

    $ guts manifest --include paths --include fs ubuntu --outfile ubuntu-guts.json


This generic "manifest" command is the main entrypoint to extract guts.

----
Diff
----

**under development**

A diff will take your container and compares it against a set of base images,
and only reveals the diff output (the executables in PATH that are special
to your container). If you don't provide a database (repository or path
on the filesystem) we use the default at ``singularityhub/shpc-guts``.

.. code-block:: console

    $ guts diff vanessa/salad

Note that this command is not officially added yet!

GitHub Action
-------------

You can use one of our GitHub actions to extract guts!


Single Image Manifest
^^^^^^^^^^^^^^^^^^^^^

For a single image (e.g., on dispatch)

.. code-block:: yaml

    name: Generate Container Guts
    on:
      workflow_dispatch:
        inputs:
          docker_uri:
            description: 'Docker identifier to generate recipe for'
            required: true
            default: "quay.io/autamus/clingo:5.5.1"
    jobs:
      generate-recipe:
        runs-on: ubuntu-latest
        name: ${{ inputs.docker_uri }}
        steps:
          - name: Checkout Repository
            uses: actions/checkout@v3
          - name: Guts for ${{ inputs.docker_uri }}
            uses: singularityhub/guts/action/manifest@main
            with:
              image: ${{ inputs.docker_uri }}
              outfile: ${{ inputs.docker_uri }}
          - name: View Output
            run: cat ${{ matrix.image }}.json


Matrix Images Manifest
^^^^^^^^^^^^^^^^^^^^^^

or for a matrix! E.g., you might want to save them nested in their directory
location.


.. code-block:: yaml

    name: Generate Container Guts
    on:
      pull_request: []
      generate-recipes:
        runs-on: ubuntu-latest
        strategy:
          max-parallel: 4
          matrix:
            image: ["ubuntu", "centos", "rockylinux:9.0", "alpine", "busybox"]

        name: Generate Matrix
        steps:
          - name: Checkout Repository
            uses: actions/checkout@v3
          - name: Guts for ${{ matrix.image }}
            uses: singularityhub/guts/action/manifest@main
            with:
              image: ${{ matrix.image }}
              outfile: ${{ matrix.image }}.json
          - name: View Output
            run: cat ${{ matrix.image }}.json


If you want the library to generate the namespace of the output files, you can
instead just provide an output directory. The example below also
shows how to get the path as an output:

.. code-block:: yaml

...

        name: Generate Matrix
        steps:
          - name: Checkout Repository
            uses: actions/checkout@v3
          - name: Guts for ${{ matrix.image }}
            uses: singularityhub/guts/action/manifest@main
            id: guts
            with:
              image: ${{ matrix.image }}
              outdir: ${{ github.workspace }}
          - name: View Output
            env:
              outfile: ${{ steps.guts.outputs.outfile }}
            run: cat ${outfile}


Diff
^^^^

The core functionality of guts is to discover new or interesting things in
the PATH, and this is the goal of diff. You can provide a guts root
path with your custom guts (e.g., the content of `shpc-guts <https://github.com/singularityhub/shpc-guts>`_
but if it's not provided, we will clone that one, which updates
base images nightly.

.. code-block:: yaml

    name: Diff Container Guts
    on:
      pull_request: []
      generate-recipes:
        runs-on: ubuntu-latest
        strategy:
          max-parallel: 4
          matrix:
            image: ["vanessa/salad"]

        name: Generate Diffs
        steps:
          - name: Checkout Repository
            uses: actions/checkout@v3
          - name: Diff for ${{ matrix.image }}
            uses: singularityhub/guts/action/diff@main
            id: guts
            with:
              image: ${{ matrix.image }}
          - name: View Output
            run: cat ${{ steps.guts.outputs.outfile }}

The above would be the same as doing:


.. code-block:: yaml

  - name: Diff for ${{ matrix.image }}
    uses: singularityhub/guts/action/diff@main
    with:
      image: ${{ matrix.image }}
      database: https://github.com/singularityhub/shpc-guts

Note that for all of the above, by default guts will be installed for you, unless you install a custom
version in a previous step.
