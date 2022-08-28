__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
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

    def exists(self, name):
        """
        Determine if a base image entry exists.
        """
        print("EXISTS")
        import IPython

        IPython.embed()
        dirname = self.source
        if self.subdir:
            dirname = os.path.join(dirname, self.subdir)
        return os.path.exists(os.path.join(dirname, name))

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
        for filename in utils.recursive_find(self.db, "*json"):
            yield filename
