__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2024, Vanessa Sochat"
__license__ = "MPL 2.0"

import os

import container_guts.utils as utils

# Default database for base image
database = "https://github.com/singularityhub/shpc-guts"

# Cache for saving guts of base images
userhome = utils.get_userhome()
guts_home = os.path.join(userhome, ".guts")
cache_dir = os.path.join(userhome, "cache")
