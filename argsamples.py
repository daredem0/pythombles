#! /bin/env python3
# -*- coding: utf-8 -*-
""" shrink_vm.py

    @Author: Florian Leuze
    @Date 07.12.2021
"""


import os, sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def do_something_cool(path, name, user, option):
    print("cool")
    print(path, name)
    print(user, option)


if __name__ == "__main__":
    description = """
    Does something amazing
    Usage:
             python3 argsamples.py -p ./cool/path -N blubb -u some_user -S
    """
    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=description, formatter_class=RawDescriptionHelpFormatter
        )
        parser.add_argument("-V", "--version", action="version", version="0.1")
        parser.add_argument(
            "-p",
            "--some-path",
            dest="some_path",
            action="store",
            default="~/",
            help="Some path",
        )
        parser.add_argument(
            "-N",
            "--some-name",
            dest="some_name",
            action="store",
            choices=["blubb", "blubber", "blibb"],
            help="Some generic name",
        )
        parser.add_argument(
            "-u",
            "--some-user",
            dest="some_user",
            action="store",
            help="Some user name",
        )
        parser.add_argument(
            "-S",
            "--some-option",
            dest="some_option",
            action="store_true",
            default=False,
            help="follows soon",
        )

        args, remaining_args = parser.parse_known_args()
        if len(remaining_args) > 0:
            print("trouble for remaining args: {}".format(remaining_args))
            if not remaining_args[0].startswith("#"):
                raise Exception("Illegal Parmaters")
        if "--help" not in args and len(sys.argv) > 1:
            do_something_cool(args.some_path, args.some_name, args.some_user, args.some_option)
        else:
            parser.print_help(sys.stdout)
    except KeyboardInterrupt as err:
        sys.exit()
    except Exception as err:
        print("Error: " + str(err.args))
        raise (err)
    sys.exit(0)
