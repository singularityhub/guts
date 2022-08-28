__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import shutil

from .. import utils
from ..logger import logger

# from .database import Database
from .container.decorator import ensure_container
from .container.base import ContainerName


class ManifestGenerator:
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
        raise NotImplementedError
        # TODO need a way to identify filesystem, likely with unique path properties
        # print(f"Generating diff for {image}")
        # tmpdir = self.extract(image, cleanup=False)
        # db = Database(database)

        # TODO need a marker to distinguish
        # print("DIFF")
        # import IPython

        # IPython.embed()

        # Only cleans up if was cloned
        # db.cleanup()
        # shutil.rmtree(tmpdir, ignore_errors=True)
        # self.container.cleanup(image)
        # return {image: self.manifests[image]}

    def extract_filesystem(self, root):
        """
        List all contents of the filesystem
        """
        print(f"Extracting filesystem at {root}")
        fs = list(utils.recursive_find(root, ".*"))
        return [x.replace(root, "") for x in fs]

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
    def extract(self, image, cleanup=True, includes=None):
        """
        Given an image, extract the temporary filesystem with metadata
        """
        # By default, include paths
        includes = includes or ["paths"]
        tmpdir = self.container.export(image, cleanup=cleanup)
        meta = self.get_manifests(os.path.join(tmpdir, "meta"))

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
            manifest[path] = list(files)
        return manifest

    def get_manifests(self, root):
        """
        Given the root of a container extracted meta directory, read all json
        configs and derive a final set of paths to explore.
        """
        manifest = {"paths": set()}
        for jsonfile in utils.recursive_find(root, "json$"):
            if "manifest" in jsonfile:
                continue
            print("Found layer config %s" % jsonfile)
            data = utils.read_json(jsonfile)

            # Fallback to config
            cfg = data.get("container_config") or data.get("config")
            if not cfg:
                continue

            # Populate paths
            for envar in cfg.get("Env") or []:
                if "PATH" in envar:
                    print(envar)
                    envar = envar.replace(" ", "").replace("PATH=", "")
                    for path in envar.split(":"):
                        manifest["paths"].add(path)
        return manifest

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[guts-manifest-generator]"
