__author__ = "Fred Jaya, Vanessa Sochat"
__copyright__ = "Copyright 2022-2024, Vanessa Sochat"
__license__ = "MPL 2.0"


import json
import os

import container_guts.utils as utils

from .base import ContainerName, ContainerTechnology
from .decorator import ensure_container


class SingularityContainerName(ContainerName):
    def parse(self, raw):
        if os.path.isabs(raw):
            """
            CVMFS image uses the raw value as the path, and parse the tool/tag from the basename.
            """
            basename = os.path.basename(raw)
            self.tool, _, self.tag = basename.partition(":")
            if not self.tag:
                self.tag = "latest"
            self.registry = None
            self.namespace = None
            self.digest = None
            self.version = None
        else:
            super().parse(raw)

    @property
    def uri(self):
        if os.path.isabs(self.raw):
            return self.raw
        return f"docker://{super().uri}"


class SingularityContainer(ContainerTechnology):
    """
    A Singularity container controller.
    """

    command = "singularity"

    def get_container(self, image):
        """
        Courtesy function to get a container from a URI.
        """
        if isinstance(image, SingularityContainerName):
            return image
        if isinstance(image, ContainerName):
            return SingularityContainerName(image.raw)
        return SingularityContainerName(image)

    @ensure_container
    def shell(self, image):
        """
        Interactive shell into a container image.
        """
        os.system(f"{self.command} shell {image.uri}")

    @ensure_container
    def cleanup(self, image):
        """
        Nothing to clean up: CVMFS images are read-only, pulled SIF files
        are left in place for reuse.
        """
        pass

    def _export_via_exec(self, image, export_dir):
        """
        Fallback export when sandbox build fails (e.g. old SIF nil-pointer crash).

        Runs 'singularity exec <image> env' to discover PATH dirs, then
        'singularity exec <image> ls <dir>' for each to enumerate executables,
        and creates empty placeholder files under export_dir so that
        explore_paths / extract_filesystem can proceed normally.
        """
        os.makedirs(export_dir, exist_ok=True)

        env_res = self.call(
            [self.command, "exec", image.uri, "env"],
            stream=False,
            allow_fail=True,
        )

        path_dirs = []
        if env_res["return_code"] == 0:
            for line in env_res["message"].splitlines():
                if line.startswith("PATH="):
                    path_dirs = [p for p in line[5:].split(":") if p]
                    break

        if not path_dirs:
            path_dirs = ["/usr/local/bin", "/usr/bin", "/bin"]

        for path_dir in path_dirs:
            ls_res = self.call(
                [self.command, "exec", image.uri, "ls", path_dir],
                stream=False,
                allow_fail=True,
            )
            if ls_res["return_code"] != 0:
                continue
            dest_dir = os.path.join(export_dir, path_dir.lstrip("/"))
            os.makedirs(dest_dir, exist_ok=True)
            for name in ls_res["message"].splitlines():
                name = name.strip()
                if name:
                    open(os.path.join(dest_dir, name), "w").close()

    @ensure_container
    def export(self, image, tmpdir=None, cleanup=True):
        """
        Export a Singularity image into a directory.

        Tries 'singularity build --sandbox' first.  Falls back to exec-based
        enumeration for old SIF formats that crash during sandbox extraction
        (e.g. nil-pointer in addResolvConfMount on Singularity 4.x).
        """
        if not tmpdir:
            tmpdir = utils.get_tmpdir()

        export_dir = os.path.join(tmpdir, "root")
        meta_dir = os.path.join(tmpdir, "meta")
        os.makedirs(meta_dir)

        # singularity build --sandbox creates export_dir itself; pre-creating it causes a FATAL error.
        res = self.call(
            [self.command, "build", "--sandbox", "--force", export_dir, image.uri],
            stream=False,
            allow_fail=True,
        )
        if res["return_code"] != 0:
            self._export_via_exec(image, export_dir)

        labels = {}
        res = self.call(
            [self.command, "inspect", "--json", image.uri],
            stream=False,
            allow_fail=True,
        )
        if res["return_code"] == 0:
            try:
                labels = (
                    json.loads(res["message"])
                    .get("data", {})
                    .get("attributes", {})
                    .get("labels", {})
                )
            except Exception:
                pass

        config = {
            "config": {
                "Env": [],
                "Labels": labels,
                "Entrypoint": None,
                "Cmd": None,
                "WorkingDir": None,
            }
        }
        utils.write_json(config, os.path.join(meta_dir, "config.json"))
        return tmpdir

    @ensure_container
    def execute(self, image, command):
        """
        Execute a command in a container image.
        """
        cmd = [self.command, "exec", image.uri] + command
        return self.call(cmd, stream=False)

    @ensure_container
    def run(self, image, command, entrypoint=None, **_):
        """
        Run a command in a container. Singularity has no detached/daemon mode
        or named containers, so those parameters are ignored.
        """
        if entrypoint:
            cmd = [self.command, "exec", image.uri, entrypoint] + command
        else:
            cmd = [self.command, "run", image.uri] + command
        print(" ".join(cmd))
        return self.call(cmd)

    @ensure_container
    def pull(self, image):
        """
        Pull a container image. Skipped if the image already exists on disk.
        """
        if os.path.exists(image.raw):
            return
        return self.call([self.command, "pull", image.uri])

    @ensure_container
    def inspect(self, image):
        """
        Inspect an image.
        """
        res = self.call([self.command, "inspect", "--json", image.uri], stream=False)
        return json.loads(res["message"])
