__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022-2024, Vanessa Sochat"
__license__ = "MPL 2.0"

import json
import os

import container_guts.utils as utils

from ..main import ManifestGenerator


def main(args, parser, extra, subparser):
    # Show args to the user
    print("         image: %s" % args.image)
    print("       outfile: %s" % args.outfile)
    print("        outdir: %s" % args.outdir)
    print("container tech: %s" % args.container_tech)
    print("      database: %s" % args.database)

    # Derive an initial manifest
    cli = ManifestGenerator(tech=args.container_tech)
    manifests = cli.diff(args.image, database=args.database)
    outfile = None

    # Default to using outfile first, then outdir if defined
    if args.outfile:
        outfile = args.outfile
    elif args.outdir:
        outfile = os.path.join(args.outdir, "%s.json" % cli.save_path(args.image))
        dirname = os.path.dirname(outfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    # If we have an output file, make sure to set step output
    if outfile:
        print(f"Saving to {outfile}...")
        print(f"::set-output name=outfile::{outfile}")
        utils.write_json(manifests, outfile)
    else:
        print(json.dumps(manifests, indent=4))
