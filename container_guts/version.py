__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2024, Vanessa Sochat"
__license__ = "MPL 2.0"

__version__ = "0.0.17"
AUTHOR = "Vanessa Sochat"
NAME = "container-guts"
EMAIL = "vsoch@users.noreply.github.com"
PACKAGE_URL = "https://github.com/singularityhub/guts"
KEYWORDS = "docker, containers, introspection"
DESCRIPTION = "Easily export container guts (executables on the path)."
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = ()

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
