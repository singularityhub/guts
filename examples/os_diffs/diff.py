#!/usr/bin/env python3

import argparse
import pandas
import json
import os
import re
import shutil
import sys
import tempfile

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="white")
sns.set(font_scale=1.4)


here = os.path.dirname(os.path.abspath(__file__))


def read_json(filename):
    with open(filename, "r") as fd:
        data = json.loads(fd.read())
    return data


def write_json(data, filename):
    with open(filename, "w") as fd:
        fd.write(json.dumps(data, indent=4))


def get_parser():
    parser = argparse.ArgumentParser(
        description="Spack Updater",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("database", help="path to database for pairwise diffs")
    return parser


def plot_heatmap(df, save_tos=None):
    f, ax = plt.subplots(figsize=(12, 12))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 3, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    p = sns.heatmap(df, linewidths=0.5, cbar=False, cmap=cmap)
    # used for heatmap
    # p.tick_params(labelsize=5)
    plt.tight_layout()
    if save_tos:
        for save_to in save_tos:
            plt.savefig(save_to)
        plt.close()


class ContainerDiffer:
    """
    Diff filesystem paths
    """

    def __init__(self, database):
        self.database = os.path.abspath(database)
        if not os.path.exists(database):
            sys.exit(f"{database} does not exist.")

    def uniques(self):
        """
        Run the diff, returning paths unique to an image (compared to another)
        """
        bases = list(recursive_find(self.database, "[.]json"))

        # Create lookup of names to paths for json
        names = {
            x.replace(self.database, "").strip("/").replace(".json", ""): x
            for x in bases
        }
        df = pandas.DataFrame(columns=list(names), index=list(names), data=0)
        uniques = {name: set() for name in names}
        for A in names:
            Apaths = self.read_fs(names[A])
            for B in names:
                if A == B:
                    continue
                Bpaths = self.read_fs(names[B])
                Apaths = [x for x in Apaths if x not in Bpaths]
                if not Apaths:
                    break
            uniques[A] = sorted(Apaths)
        return uniques

    def filter_hidden(self, paths):
        """
        Filter out hidden paths that might be temporary.
        """
        finals = []
        for path in paths:
            if any(x.startswith(".") for x in path.split(os.sep)):
                continue
            finals.append(path)
        return finals

    def diff(self):
        """
        Run the diff
        """
        bases = list(recursive_find(self.database, "[.]json"))

        # Create lookup of names to paths for json
        names = {
            x.replace(self.database, "").strip("/").replace(".json", ""): x
            for x in bases
        }
        df = pandas.DataFrame(columns=list(names), index=list(names), data=0)

        for A in names:
            for B in names:
                if A == B:
                    df.loc[A, B] = 1

                # Crappy way to see if we've already seen
                elif df.loc[A, B] != 0:
                    continue
                else:
                    df.loc[A, B] = self.calculate_diff(names[A], names[B])
        return df

    def read_fs(self, jsonA):
        """
        Read filesystem entries and filter out hidden paths
        """
        A = read_json(jsonA)
        paths = set(list(A.values())[0]["fs"])
        return self.filter_hidden(paths)

    def calculate_diff(self, jsonA, jsonB):
        """
        Calculate the set difference

        intersection of A and B
        -------------------------
        union of items in A and B
        """
        A = set(self.read_fs(jsonA))
        B = set(self.read_fs(jsonB))

        return len(A.intersection(B)) / len(A.union(B))


def recursive_find(base, pattern=None):
    """
    Find filenames that match a particular pattern, and yield them.
    """
    # We can identify modules by finding module.lua
    for root, folders, files in os.walk(base):
        for file in files:
            fullpath = os.path.abspath(os.path.join(root, file))

            if pattern and not re.search(pattern, fullpath):
                continue

            yield fullpath


def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Show args to the user
    print("   database: %s" % args.database)

    cli = ContainerDiffer(args.database)
    df = cli.diff()
    df.to_csv("os-diffs.csv")

    uniques = cli.uniques()
    write_json(uniques, "unique-paths.json")

    # Create matrix with seaborn
    plot_heatmap(df, ["os-diffs.svg", "os-diffs.png"])


if __name__ == "__main__":
    main()
