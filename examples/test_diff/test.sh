#!/bin/bash

# Note that a single diff does comparisons of an image with an entire set of bases
guts diff vanessa/salad --outfile vanessa-salad-diff.json
guts diff autamus/clingo:5.5.1 --outfile autamus-clingo-diff.json
guts diff quay.io/biocontainers/samtools:0.1.19--2 --outfile biocontainers-samtools.json

# A double diff can eventually do a clean subtraction (not implemnted yet)
