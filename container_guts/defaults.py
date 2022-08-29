__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import container_guts.utils as utils
import os

# Default database for base image
database = "https://github.com/singularityhub/shpc-guts"

# Cache for saving guts of base images
userhome = utils.get_userhome()
guts_home = os.path.join(userhome, ".guts")
cache_dir = os.path.join(userhome, "cache")
