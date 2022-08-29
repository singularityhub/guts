#!/bin/bash

# Note that a single diff does comparisons of an image with an entire set of bases
guts diff vanessa/salad --outfile vanessa-salad-diff.json
guts diff autamus/clingo:5.5.1 --outfile autamus-clingo-diff.json

# A double diff can eventually do a clean subtraction (not implemnted yet)
