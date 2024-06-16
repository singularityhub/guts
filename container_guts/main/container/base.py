__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2024, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import re
import shutil

import container_guts.main.templates as templates
import container_guts.utils as utils
from container_guts.logger import logger


class ContainerName:
    """
    Parse a container name into named parts
    """

    def __init__(self, raw):
        self.raw = raw
        self.registry = None
        self.repository = None
        self.tool = None
        self.version = None
        self.digest = None
        self.parse(raw)

    def __str__(self):
        return self.uri

    @property
    def container_name(self):
        """
        Derive a container name from the uri
        """
        return self.uri.replace("/", "-").replace(":", "-")

    @property
    def uri(self):
        """
        Show the full uri
        """
        uri = self.tool
        if self.namespace:
            uri = f"{self.namespace}/{uri}"

        # Can only add registry given namespace
        if self.registry and self.namespace:
            uri = f"{self.registry}/{uri}"
        if self.tag:
            uri = f"{uri}:{self.tag}"
        return uri

    @property
    def path(self):
        """
        A path for an image
        """
        return self.uri.replace(":", os.sep)

    def parse(self, raw):
        """
        Parse a name into known pieces
        """
        match = re.search(templates.docker_regex, raw)
        if not match:
            logger.exit("%s does not match a known identifier pattern." % raw)
        for key, value in match.groupdict().items():
            value = value.strip("/") if value else None
            setattr(self, key, value)

        # Set defaults
        if not self.tag:
            self.tag = "latest"
        if not self.namespace:
            self.namespace = "library"
        if not self.registry:
            self.registry = "docker.io"


class ContainerTechnology:
    """
    A base class for a container technology
    """

    def __init__(self):
        if hasattr(self, "command") and not shutil.which(self.command):
            logger.exit(
                "%s is required to use the '%s' base."
                % (self.command.capitalize(), self.command)
            )

    def call(self, command, stream=True, allow_fail=False):
        """
        Call a command and check for error.
        """
        res = utils.run_command(command, stream=stream)
        if res["return_code"] != 0 and not allow_fail:
            logger.exit("There was an issue running %s" % " ".join(command))
        return res

    def __str__(self):
        return str(self.__class__.__name__)
