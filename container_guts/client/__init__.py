#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2024, Vanessa Sochat"
__license__ = "MPL 2.0"

import argparse
import os
import sys

import container_guts
from container_guts.logger import setup_logger


def get_parser():
    parser = argparse.ArgumentParser(
        description="Guts",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )

    description = "actions for Guts"
    subparsers = parser.add_subparsers(
        help="actions",
        title="actions",
        description=description,
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", description="show software version")

    manifest = subparsers.add_parser(
        "manifest",
        description="export manifest of guts!",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    diff = subparsers.add_parser(
        "diff",
        description="take a diff of your container against a guts database.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    similar = subparsers.add_parser(
        "similar",
        description="calculate similarity of your container against a guts database.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    for command in [diff, similar]:
        command.add_argument(
            "--db",
            "--database",
            help="Database root (of json files) to use, either filesystem or git URL to clone",
            dest="database",
        )

    for command in manifest, diff, similar:
        command.add_argument(
            "-i",
            "--include",
            help="Type of guts to include in extraction (defaults to paths)",
            dest="guts",
            choices=["fs", "paths"],
            action="append",
            default=[],
        )
        command.add_argument(
            "-c",
            "--container-tech",
            dest="container_tech",
            help="container technology to use for exporting",
            choices=["docker"],
            default="docker",
        )
        command.add_argument(
            "image",
            help="Container URI to parse",
        )
        command.add_argument(
            "-o",
            "--outfile",
            help="Output manifest file, over-rides outdir",
            dest="outfile",
        )
        command.add_argument(
            "--outdir",
            help="Root to write output structure, not used if not set.",
        )
    return parser


def run():
    """
    Entrypoint to generating container guts
    """
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """
        version = container_guts.__version__

        print("\nGuts Client v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(container_guts.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    # Does the user want a shell?
    if args.command == "manifest":
        from .manifest import main
    elif args.command == "diff":
        from .diff import main
    elif args.command == "similar":
        from .similar import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args, parser=parser, extra=extra, subparser=helper)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)


if __name__ == "__main__":
    run()
