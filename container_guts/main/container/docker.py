__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022-2024, Vanessa Sochat"
__license__ = "MPL 2.0"


import json
import os
import sys

import container_guts.utils as utils

from .base import ContainerName, ContainerTechnology
from .decorator import ensure_container


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
    def cleanup(self, image):
        """
        Stop and remove an image.
        """
        self.call([self.command, "stop", image.container_name], allow_fail=True)
        self.call(
            [self.command, "rm", "--force", image.container_name], allow_fail=True
        )
        # TODO should have an arg to keep this (it's annoying to delete)
        self.call([self.command, "rmi", "--force", image.uri], allow_fail=True)

    @ensure_container
    def export(self, image, tmpdir=None, cleanup=True):
        """
        Export a docker image into .tar -> directory

        Since we also want a filesystem from a running container, we use
        save and export dually. This could be adjusted to be completely
        static and just use save, if desired.
        """
        if not tmpdir:
            tmpdir = utils.get_tmpdir()

        # Prepare paths for saving
        save = os.path.join(tmpdir, f"{image.container_name}-save.tar")
        export = os.path.join(tmpdir, f"{image.container_name}.tar")
        export_dir = os.path.join(tmpdir, "root")
        save_dir = os.path.join(tmpdir, "meta")

        self.pull(image.uri)
        self.run(
            image.uri, ["-f", "/dev/null"], entrypoint="tail", name=image.container_name
        )

        # This is the filesystem (export done by container name)
        self.call([self.command, "export", image.container_name, "--output", export])

        # This will have the config
        self.call([self.command, "save", image.uri, "--output", save])

        # Diff does not cleanup so we can still inspect image
        if cleanup:
            self.cleanup(image)

        for tar in export, save:
            if not os.path.exists(tar):
                sys.exit(f"There was an issue exporting/saving to {tar}")

        for dirname in save_dir, export_dir:
            os.makedirs(dirname)

        try:
            self.call(["tar", "--ignore-failed-read", "-xf", export, "-C", export_dir])
            self.call(["tar", "--ignore-failed-read", "-xf", save, "-C", save_dir])
        except Exception:
            self.call(["tar", "-xf", export, "-C", export_dir])
            self.call(["tar", "-xf", save, "-C", save_dir])

        return tmpdir

    @ensure_container
    def execute(self, image, command):
        """
        Exec a command to a running container.
        """
        cmd = [self.command, "exec", image.container_name] + command
        print(" ".join(cmd))
        return self.call(cmd, stream=False)

    @ensure_container
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
        cmd.append(image.uri)
        cmd += command
        print(" ".join(cmd))
        return self.call(cmd)

    @ensure_container
    def pull(self, image):
        """
        Pull a container by name
        """
        return self.call([self.command, "pull", image.uri])

    @ensure_container
    def tag(self, image, tag_as):
        """
        Given a container URI, tag as something else.
        """
        return self.call([self.command, "tag", image.uri, tag_as])

    @ensure_container
    def inspect(self, image):
        """
        Inspect an image
        """
        res = self.call([self.command, "inspect", image.uri], stream=False)
        raw = res["message"]
        return json.loads(raw)
