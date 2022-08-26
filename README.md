# Container Guts!

Action to derive executables on the PATH inside a container. 🤓

## Usage


### Manual

You can test manually! If you provide an output file, it will save to it,
otherwise it will print to the screen.

```bash
$ python manifest/scripts/prepare_manifests.py ubuntu
```
```bash
$ python manifest/scripts/prepare_manifests.py --outfile ubuntu-guts.json ubuntu
```

The example [ubuntu-guts.json](ubuntu-guts.json) is provided.

### GitHub Actions
For a single image (e.g., on dispatch)

```yaml
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
    permissions:
      packages: read
    name: ${{ inputs.docker_uri }}
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3
      - name: Guts for ${{ inputs.docker_uri }}
        uses: ./manifest
        with:
          image: ${{ inputs.docker_uri }}
          outfile: ${{ inputs.docker_uri }}
      - name: View Output
        run: cat ${{ matix.image }}.json
```

or for a matrix! E.g., you might want to save them nested in their directory
location.

```yaml
name: Generate Container Guts
on:
  pull_request: []
  generate-recipes:
    runs-on: ubuntu-latest
    permissions:
      packages: read
    strategy:
      max-parallel: 4
      matrix:
        image: ["ubuntu", "centos", "rockylinux", "alpine", "busybox"]

    name: Generate Matrix
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3
      - name: Guts for ${{ inputs.docker_uri }}
        uses: ./manifest
        with:
          image: ${{ matrix.image }}
          outfile: ${{ matrix.image }}.json
      - name: View Output
        run: cat ${{ matrix.image }}.json
