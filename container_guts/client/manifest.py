__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import json

import container_guts.utils as utils
from ..main import ManifestGenerator


def main(args, parser, extra, subparser):

    # Show args to the user
    print("         image: %s" % args.image)
    print("       outfile: %s" % args.outfile)
    print("container tech: %s" % args.container_tech)

    cli = ManifestGenerator(tech=args.container_tech)
    manifests = cli.run(args.image)
    if args.outfile:
        print(f"Saving to {args.outfile}...")
        utils.write_json(manifests, args.outfile)
    else:
        print(json.dumps(manifests, indent=4))
