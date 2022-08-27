__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import shutil

from .. import utils
from ..logger import logger


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

    def save_path(self, image):
        """
        Derive a save path, if desired.
        """
        return self.container.save_path(image)

    def run(self, image):
        """
        Run the generator to create a paths manifest.
        """
        print(f"Adding {image} to paths manifest")
        tmpdir = self.container.export(image)
        paths = self.get_paths(os.path.join(tmpdir, "meta"))
        print(f"\nSearching {image}")
        self.manifests[image] = self.explore_paths(
            os.path.join(tmpdir, "root"), paths=paths
        )
        shutil.rmtree(tmpdir, ignore_errors=True)
        return {image: self.manifests[image]}

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

    def get_paths(self, root):
        """
        Given the root of a container extracted meta directory, read all json
        configs and derive a final set of paths to explore.
        """
        paths = set()
        for jsonfile in utils.recursive_find(root, "json$"):
            if "manifest" in jsonfile:
                continue
            print("Found layer config %s" % jsonfile)
            data = utils.read_json(jsonfile)

            # Fallback to config
            cfg = data.get("container_config") or data.get("config")
            if not cfg or "Env" not in cfg:
                continue

            for envar in cfg.get("Env") or []:
                if "PATH" in envar:
                    print(envar)
                    envar = envar.replace(" ", "").replace("PATH=", "")
                    for path in envar.split(":"):
                        paths.add(path)
        return paths

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[guts-manifest-generator]"
