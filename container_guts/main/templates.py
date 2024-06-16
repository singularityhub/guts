__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2024, Vanessa Sochat"
__license__ = "MPL 2.0"

import re

docker_regex = re.compile(
    "(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
    "(?P<namespace>(?:[^:@/]+/)+)?"
    "(?P<tool>[^:@/]+)"
    "(?::(?P<tag>[^:@]+))?"
    "(?:@(?P<digest>.+))?"
    "$"
)
