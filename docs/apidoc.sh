#!/bin/bash
rm api_reference/*.rst
sphinx-apidoc -o api_reference/ ../container_guts
