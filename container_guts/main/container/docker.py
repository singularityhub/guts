__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import json
import os
import sys

import container_guts.utils as utils
from .decorator import ensure_container

from .base import ContainerTechnology, ContainerName


class DockerContainer(ContainerTechnology):
    """
    A Docker container controller.
    """

    command = "docker"

    @ensure_container
    def shell(self, image):
        """
        Interactive shell into a container image.
        """
        os.system(
            "%s run -it --rm --entrypoint %s %s"
            % (self.command, self.shell_path, image)
        )

    def get_container(self, image):
        """
        Courtesy function to get a container from a URI.
        """
        if isinstance(image, ContainerName):
            return image
        return ContainerName(image)

    @ensure_container
    def save_path(self, image):
        """
        Derive a save path, if desired.
        """
        return image.path

    @ensure_container
    def export(self, image, tmpdir=None):
        """
        Export a docker image into .tar -> directory

        Since we also want a filesystem from a running container, we use
        save and export dually. This could be adjusted to be completely
        static and just use save, if desired.
        """
        if not tmpdir:
            tmpdir = utils.get_tmpdir()

        # Prepare paths for saving
        prefix = image.uri.replace("/", "-").replace(":", "-")
        save = os.path.join(tmpdir, f"{prefix}-save.tar")
        export = os.path.join(tmpdir, f"{prefix}.tar")
        export_dir = os.path.join(tmpdir, "root")
        save_dir = os.path.join(tmpdir, "meta")

        self.pull(image.uri)
        self.run(image.uri, ["-f", "/dev/null"], entrypoint="tail", name=prefix)

        # This is the filesystem (export done by container name)
        self.call([self.command, "export", prefix, "--output", export])

        # This will have the config
        self.call([self.command, "save", image.uri, "--output", save])
        self.call([self.command, "stop", prefix])
        self.call([self.command, "rm", "--force", prefix])
        self.call([self.command, "rmi", "--force", image.uri])

        for tar in export, save:
            if not os.path.exists(tar):
                sys.exit(f"There was an issue exporting/saving to {tar}")

        for dirname in save_dir, export_dir:
            os.makedirs(dirname)
        self.call(["tar", "-xf", export, "-C", export_dir])
        self.call(["tar", "-xf", save, "-C", save_dir])
        return tmpdir

    def run(self, image, command, entrypoint=None, name=None, detached=True):
        """
        Run a container detached, assuming the entrypoint goes to tail /dev/null.
        """
        cmd = [self.command, "run", "--rm"]
        if name:
            cmd += ["--name", name]
        if entrypoint:
            cmd += ["--entrypoint", entrypoint]
        if detached:
            cmd.append("-d")
        cmd.append(image)
        cmd += command
        print(" ".join(cmd))
        return self.call(cmd)

    def pull(self, image):
        """
        Pull a container by name
        """
        return self.call([self.command, "pull", image])

    def tag(self, image, tag_as):
        """
        Given a container URI, tag as something else.
        """
        return self.call([self.command, "tag", image, tag_as])

    def inspect(self, image):
        """
        Inspect an image
        """
        res = self.call([self.command, "inspect", image], stream=False)
        raw = res["message"]
        return json.loads(raw)
