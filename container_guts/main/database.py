__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2024, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import shutil
import subprocess as sp

import container_guts.utils as utils

from ..defaults import database as default_database


class Database:
    def __init__(self, source=None):
        self.source = source or default_database
        self.do_cleanup = False
        self.set_database()

    @staticmethod
    def executable_names(entry):
        """
        Basenames of the executables on PATH in a manifest.

        A manifest's "paths" already maps a PATH directory to the basenames it
        holds, so there is no path manipulation to do here. Keys that are not
        absolute paths are skipped: _parse_paths matches any environment
        variable *containing* "PATH", so real manifests carry keys such as
        "MODULE/etc/lmod/modules" and "LD_LIBRARY_/.singularity.d/libs".
        """
        return {
            name
            for directory, names in (entry.get("paths") or {}).items()
            if directory.startswith(os.sep)
            for name in names
        }

    def diff(self, manifest):
        """
        Do a diff of the image against the database.

        This is fairly stupid, but I found it works well to just subtract all
        the base images, and meaningful added stuff is left.

        Subtracting whole paths is not enough on its own. Base images disagree
        about where they keep the same executable - busybox puts its applets in
        /bin, while images built on it symlink them into /sbin and /usr/sbin,
        and conda ships its own copies of ncurses tools under /usr/local/bin.
        Those never cancel out as strings, so the base binaries come back out
        of the diff looking unique. An executable on PATH is identified by its
        name, so also drop anything whose basename belongs to a base image, and
        report those separately as "shadowed_paths" so a caller that knows
        better (e.g. a tool that really is named "sort") can put one back.

        "unique_fs" stays a plain path-level difference - it is a filesystem
        comparison rather than a statement about executables, and similar()
        scores off it.
        """
        fs = set(manifest["fs"])
        count = len(fs)
        base_names = set()
        for data in self.iter_containers():
            base_image = list(data.keys())[0]
            entry = list(data.values())[0]
            fs = fs.difference(set(entry["fs"]))
            base_names.update(self.executable_names(entry))
            difference = count - len(fs)
            print(f"{base_image}: removed {difference} shared paths.")
            count = len(fs)

        paths = sorted(
            {"%s%s%s" % (k, os.sep, x) for k, v in manifest["paths"].items() for x in v}
        )

        # Filter down to thoses in PATH or entrypoint
        on_path = [x for x in fs if x in manifest.get("entrypoint", []) or x in paths]
        shadowed = [x for x in on_path if os.path.basename(x) in base_names]
        return {
            "unique_paths": sorted(set(on_path).difference(shadowed)),
            "shadowed_paths": sorted(shadowed),
            "unique_fs": sorted(list(fs)),
        }

    def similar(self, manifest):
        """
        Find similar images against the database.
        """
        # Get and subtract all paths that are unique to the image
        diff = self.diff(manifest)

        # This is the image, minus all unique / different paths
        fs = {x for x in manifest["fs"] if x not in diff["unique_fs"]}

        scores = {}
        count = len(fs)
        top_score = None
        most_similar_image = None
        for data in self.iter_containers():
            base_image = list(data.keys())[0]
            base_fs = set(list(data.values())[0]["fs"])
            # Total that are in common / total
            intersection = fs.intersection(base_fs)
            score = len(intersection) / count
            if top_score is None or score > top_score:
                top_score = score
                most_similar_image = base_image
            scores[base_image] = {
                "intersection_div_total_score": score,
                "intersection": len(intersection),
                "total_non_unique_image": count,
                "base_image": base_image,
            }

        # Add the most similar image
        scores["most_similar"] = {"base_image": most_similar_image, "score": top_score}
        return scores

    def set_database(self):
        """
        Ensure we have a database on the local filesystem.
        """
        if os.path.exists(self.source):
            self.db = self.source
            return

        # Remote - clone to make local
        if "http" in self.source:
            self.db = self.clone()

    def cleanup(self):
        if self.do_cleanup and os.path.exists(self.db):
            shutil.rmtree(self.db)

    def clone(self, tmpdir=None):
        """
        Clone the known source URL to a temporary directory
        """
        tmpdir = tmpdir or utils.get_tmpdir()

        cmd = ["git", "clone", "--depth", "1"]
        cmd += [self.source, tmpdir]
        try:
            sp.run(cmd, check=True)
        except sp.CalledProcessError as e:
            raise ValueError("Failed to clone repository {}:\n{}", self.source, e)
        self.do_cleanup = True
        return tmpdir

    def iter_containers(self):
        """
        yield container files
        """
        for filename in utils.recursive_find(self.db, "[.]json"):
            yield utils.read_json(filename)
