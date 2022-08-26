#!/usr/bin/env python3

import argparse
import hashlib
import json
import fnmatch
import requests
import tempfile
import re
import shutil
import subprocess
import sys
import os

def recursive_find(base, pattern="*json"):
    for root, _, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)

def write_json(data, filename):
    """
    Write json to file
    """
    with open(filename, 'w') as fd:
        fd.write(json.dumps(data, indent=4))

def read_file(filename):
    """
    Read content from file
    """
    with open(filename, "r") as fd:
        content = fd.read()
    return content

def read_json(input_file):
    """
    Read json
    """
    with open(input_file, "r") as filey:
        data = json.loads(filey.read())
    return data

class ManifestGenerator:
    def __init__(self, outfile):
        self.image = image
        self.check()

    def check(self):
        if not shutil.which('docker'):
            sys.exit('docker not found, required for export.')

    def run(self):
        """
        Run the generator to create a paths manifest.
        """
        # Organized by URI for easier composition
        manifests = {}
        print(f"Adding {self.image} to paths manifest")
        tmpdir = self.docker_export(self.image)
        paths = self.get_paths(os.path.join(tmpdir, "meta"))
        print(f"\nSearching {self.image}")
        manifests[self.image] = self.explore_paths(os.path.join(tmpdir, "root"), paths=paths)
        shutil.rmtree(tmpdir)
        return manifests

    def explore_paths(self, root, paths):
        """
        Find executables under a path.
        """
        manifest = {}        
        for path in paths:
            files = set()
            root_path = os.path.join(root, path.strip('/'))
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
        for jsonfile in recursive_find(root, "*json"):
            if "manifest" in jsonfile:
                continue
            print("Found layer config %s" % jsonfile)
            cfg = read_json(jsonfile)
            for envar in cfg['container_config']['Env']:
                print(envar)
                if "PATH" in envar:
                    envar = envar.replace('PATH=', '')
                    for path in envar.split(':'):
                        paths.add(path)
        return paths

    def docker_export(self, image, tmpdir=None):
        """
        Export a docker image into .tar -> directory
        """
        if not tmpdir:
            tmpdir = tempfile.mkdtemp()
        prefix = image.replace('/', '-').replace(':', '-')
        save = os.path.join(tmpdir, f"{prefix}-save.tar")
        export = os.path.join(tmpdir, f"{prefix}.tar")
        export_dir = os.path.join(tmpdir, "root")
        save_dir = os.path.join(tmpdir, "meta")

        self.call(["docker", "pull", image])

        self.call(["docker", "run", "--rm", "--name", prefix, "-d", image, "tail", "-f", "/dev/null"])

        # This is the filesystem
        self.call(["docker", "export", prefix, "--output", export])
        
        # This will have the config
        self.call(["docker", "save", image, "--output", save])
        self.call(["docker", "stop", prefix])
        self.call(["docker", "rm", "--force", prefix])
        self.call(["docker", "rmi", "--force", image])
        
        for tar in export, save:
            if not os.path.exists(tar):
                sys.exit(f"There was an issue exporting/saving to {tar}")

        for dirname in save_dir, export_dir:          
            os.makedirs(dirname)
        self.call(["tar", "-xvf", export, "-C", export_dir])
        self.call(["tar", "-xvf", save, "-C", save_dir])
        return tmpdir
        

    def call(self, cmd):
        p = subprocess.call(cmd)
        if p != 0:
            sys.exit("Issue running command %s" % " ".join(cmd))

def get_parser():
    parser = argparse.ArgumentParser(
        description="Manifest Parser",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--image",
        help="Container URI to parse",
    )
    parser.add_argument(
        "-o"
        "--outfile",
        help="Output manifest file",
        default="paths-manifest.json",
        dest="outfile",
    )
    return parser


def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show args to the user
    print("       image: %s" % args.image)
    print("     outfile: %s" % args.outfile)

    gen = ManifestGenerator()
    manifests = gen.run(args.image)
    if args.outfile:
        write_json(manifests, args.outfile)        

if __name__ == "__main__":
    main()