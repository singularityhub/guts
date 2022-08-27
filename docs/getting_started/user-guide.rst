.. _getting_started-user-guide:

==========
User Guide
==========


If you haven't installed Guts yet, you should read :ref:`getting_started-installation` first.

Commands
========

Guts currently has just one client command, "manifest" to 
get a manifest of executables on the ``PATH``!

----
Guts
----

Using guts on the command line is the easiest way to test it manually.
By default, the results will be printed to the screen:

.. code-block:: console

    $ guts manifest ubuntu

If you provide an output file, it will save to it:

.. code-block:: console

    $ guts manifest --outfile ubuntu-guts.json ubuntu

We currently have a generic "manifest" command, as there is only one thing
to export. If we add more things, this can be extended.

GitHub Action
-------------

You can use one of our GitHub actions to extract guts!


Single Image
^^^^^^^^^^^^

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
            uses: singularityhub/guts/manifest@main
            with:
              image: ${{ inputs.docker_uri }}
              outfile: ${{ inputs.docker_uri }}
          - name: View Output
            run: cat ${{ matrix.image }}.json

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
            uses: singularityhub/guts/manifest@main
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
            uses: singularityhub/guts/manifest@main
            id: guts
            with:
              image: ${{ matrix.image }}
              outdir: ${{ github.workspace }}
          - name: View Output
            env:
              outfile: ${{ steps.guts.outputs.outfile }}
            run: cat ${outfile}


Note that by default guts will be installed for you, unless you install a custom
version in a previous step.
