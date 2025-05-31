__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2024, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import shutil

from .. import utils
from ..logger import logger
from .container.base import ContainerName
from .container.decorator import ensure_container
from .database import Database


class ManifestGenerator:
    """
    Generate a Guts manifest.
    """

    def __init__(self, tech="docker"):
        self.init_container_tech(tech)
        self.manifests = {}

    def init_container_tech(self, tech):
        """
        Add the container operator
        """
        if tech == "docker":
            from .container import DockerContainer
        else:
            logger.exit(f"Container technology {tech} is not supported.")
        self.container = DockerContainer()

    @ensure_container
    def save_path(self, image):
        """
        Derive a save path, if desired.
        """
        return image.path

    def get_container(self, image):
        """
        Courtesy function to get a container from a URI.
        """
        if isinstance(image, ContainerName):
            return image
        return ContainerName(image)

    @ensure_container
    def diff(self, image, database=None):
        """
        Generate a manifest for an image and diff against likely
        """
        print(f"Generating diff for {image}")
        tmpdir = self.extract(image, cleanup=False, includes=["paths", "fs"])
        db = Database(database)

        # Catch the error so we clean up the running container
        try:
            result = db.diff(self.manifests[image.uri])
        except Exception:
            self.container.cleanup(image)
            return

        # Only cleans up if was cloned
        db.cleanup()
        shutil.rmtree(tmpdir, ignore_errors=True)
        self.container.cleanup(image)
        return {image.uri: {"diff": result}}

    @ensure_container
    def similar(self, image, database=None):
        """
        Generate a manifest for an image and similarity scores
        """
        print(f"Generating similarity for {image}")
        tmpdir = self.extract(image, cleanup=False, includes=["paths", "fs"])
        db = Database(database)

        # Catch the error so we clean up the running container
        try:
            result = db.similar(self.manifests[image.uri])
        except Exception:
            self.container.cleanup(image)
            return

        # Only cleans up if was cloned
        db.cleanup()
        shutil.rmtree(tmpdir, ignore_errors=True)
        self.container.cleanup(image)
        return {image.uri: {"similar": result}}

    def extract_filesystem(self, root):
        """
        List all contents of the filesystem
        """
        print(f"Extracting filesystem at {root}")
        fs = list(utils.recursive_find(root, ".*"))
        return sorted([x.replace(root, "") for x in fs])

    @ensure_container
    def run(self, image, includes=None):
        """
        Run the generator to create a paths manifest.
        """
        print(f"Adding {image} to guts manifest")
        tmpdir = self.extract(image, includes=includes)
        shutil.rmtree(tmpdir, ignore_errors=True)
        return {image.uri: self.manifests[image.uri]}

    @ensure_container
    def trace(self, image, paths, cleanup=True):
        """
        Find and trace a binary in the container

        Paths must be provided, either the full path or a basename.
        """
        print(f"Looking for {len(paths)} path(s) in image")
        tmpdir = self.container.export(image, cleanup=False)

        # Results will be lookup with binary path and links
        results = {}
        for path in paths:

            # We rely on the user to provide something on the path OR a fullpath
            links = self.container.execute(image, ["ldd", path])
            if links["return_code"] != 0:
                print(links["message"])
                return
            links = [
                x.replace("\t", "") for x in links["message"].split("\n") if x.strip()
            ]
            results[path] = [
                x.split("(")[0].split("=> ")[-1] for x in links if "=>" in x
            ]

        if cleanup:
            self.container.cleanup(image)

        # Assume that something that isn't linked won't be mapped
        shutil.rmtree(tmpdir, ignore_errors=True)
        return results

    @ensure_container
    def get_environment_paths(self, image):
        """
        Get environment paths.
        """
        paths = []
        envs = self.container.execute(image, ["env"])
        if envs["return_code"] != 0:
            return
        for line in envs["message"].split("\n"):
            paths += self._parse_paths(line)
        return paths

    @ensure_container
    def extract(self, image, cleanup=True, includes=None):
        """
        Given an image, extract the temporary filesystem with metadata
        """
        # By default, include paths
        includes = includes or ["paths"]
        tmpdir = self.container.export(image, cleanup=False)
        meta = self.get_manifests(os.path.join(tmpdir, "meta"))

        # Get a PATH from the running container
        [meta["paths"].add(x) for x in self.get_environment_paths(image)]
        if cleanup:
            self.container.cleanup(image)

        # The manifest generator keeps a record of the image
        print(f"\nSearching {image}")
        if image.uri not in self.manifests:
            self.manifests[image.uri] = {}

        # Root of filesystem
        root = os.path.join(tmpdir, "root")

        # Only extract includes we are asked for
        for include in includes:
            if include == "paths":
                data = self.explore_paths(root, paths=meta["paths"])
            elif include in ["fs", "filesystem"]:
                data = self.extract_filesystem(root)
            else:
                logger.warning(f"Data type {include} is not recognized.")
                continue
            self.manifests[image.uri][include] = data

        for attr in ["entrypoint", "cmd", "workingdir", "labels"]:
            if attr in meta:
                self.manifests[image.uri][attr] = meta[attr]

        return tmpdir

    def explore_paths(self, root, paths):
        """
        Find executables under a path.
        """
        manifest = {}
        for path in paths:
            files = set()
            root_path = os.path.join(root, path.strip("/"))
            if os.path.exists(root_path):
                print(f"... {path}")
                [files.add(x) for x in os.listdir(root_path)]
            manifest[path] = sorted(list(files))
        return manifest

    def _parse_paths(self, envar):
        """
        Parse a string environment variable for paths.
        """
        paths = []
        # Cut out early given empty string
        if not envar:
            return paths
        if "PATH" in envar:
            print(envar)
            envar = envar.replace(" ", "").replace("PATH=", "").strip()
            for path in envar.split(":"):
                if not path:
                    continue
                paths.append(path)
        return paths

    def get_manifests(self, root):
        """
        Given the root of a container extracted meta directory, read all json
        configs and derive a final set of paths to explore.
        """
        manifest = {"paths": set()}
        for jsonfile in utils.recursive_find(root, "json$"):
            data = utils.read_json(jsonfile)
            if "manifest" in jsonfile:
                continue
            print("Found layer config %s" % jsonfile)

            # Fallback to config
            cfg = data.get("container_config") or data.get("config")
            if not cfg:
                continue

            # Get entrypoint, command, labels
            for attr in ["Entrypoint", "Cmd", "WorkingDir", "Labels"]:
                if cfg.get(attr) and attr.lower() not in manifest:
                    manifest[attr.lower()] = cfg[attr]

            # Populate paths
            for envar in cfg.get("Env") or []:
                [manifest["paths"].add(x) for x in self._parse_paths(envar)]
        return manifest

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[guts-manifest-generator]"
