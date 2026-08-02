#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#

from posixpath import curdir
import sys
import argparse
from pathlib import Path


### - pyLnLib modules
from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger
C=get_colors()
logger=get_logger()

# ##################################################
# # parseInput
# ##################################################
def parseInput():
    global v


    def common_options(parser):
        logger_levels: list[str]=logger.get_log_levels()
        common = parser.add_argument_group(f'{C.white} --------- Common options{C.reset}')
        common.add_argument('--go',            action='store_true', help=f'{C.green}specify if command must be executed. {v.default}')
        common.add_argument('--display-args',  action='store_true', help=f'{C.green}Display arguments {v.default}')
        common.add_argument("--vars", action="store_true", help="Display project variables")
        common.add_argument("--edit", action="store_true", help="Edit this script")
        common.add_argument( "--console-log-level",
                                metavar='',
                                type=str.lower,
                                required=False,
                                default='info',
                                help=f"""{C.green}set console logger level:
                                        {logger_levels}{v.default}
                                        \n\n""".replace('  ', '')
                            )

    def git_flags(parser):
        flags = parser.add_argument_group(f'{C.white} --------- git flags{C.reset}')
        flags.add_argument("--tag", action="store_true", help=f"{v.default}")
        flags.add_argument("--push", action="store_true", help=f"{v.default}")
        flags.add_argument("--status", action="store_true", help=f"{v.default}")
        # flags.add_argument("--scan", action="store_true", help=f"scan directoried for searching git repositories{v.default}")
        # flags.add_argument("--all", action="store_true", help=f"process all repositories defined in config file {v.default}")
        flags.add_argument("--ziplib", action="store_true", help=f"zip pyLnLib to be saved in git {v.default}")

    def git_commands(parser):
        commands=parser.add_argument_group(f'{C.white} --------- git commands{C.reset}')
        commands.add_argument("--new-branch",  metavar='', default=None, type=str, help="Branch name")
        commands.add_argument("--del-branch", action="store_true", help="""BR='old_branch' && git branch -d ${BR} && git push gitHub --delete ${BR}""")
        commands.add_argument("--list-commands", action="store_true", help="list of some useful commands.")

    def version_flags(parser):
        group=parser.add_argument_group(f'{C.white} --------- release options{C.reset}')
        versionn=group.add_mutually_exclusive_group(required=False)
        versionn.add_argument("--major", action="store_true", help=f"increments x._._ {v.default}")
        versionn.add_argument("--minor", action="store_true", help=f"increments _.x._ {v.default}")
        versionn.add_argument("--patch", action="store_true", help=f"increments _._.x {v.default}")
        versionn.add_argument("--version", metavar='', default=None, type=str, help=f"Versione manuale (es 1.2.3) {v.default}")


    # --- main
    from datetime import datetime
    from types import SimpleNamespace
    now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    v=SimpleNamespace(
        default_color=C.yellow,
        metavar_optional=f'{C.white}<optional>{C.reset}',
        metavar_mandatory=f'{C.white}<mandatory>{C.reset}',
    )
    v.default=f'{v.default_color}(default: %(default)s){C.reset}\n\n'

    this_dir = Path(curdir).resolve().name
    parser = argparse.ArgumentParser(description=f"Release tool {C.whiteH}{sys.argv[0]}{C.reset}")
    parser.add_argument("--project", metavar='', type=str, default=this_dir, help=f"project_name | all (default: %(default)s)")
    parser.add_argument("description", metavar='', nargs="?", default=f"update on {now}", type=str, help="Description")
    git_flags(parser)
    version_flags(parser)
    git_commands(parser)
    common_options(parser)
    args = parser.parse_args()


    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print(f'input arguments: {json_data}')
        sys.exit(0)



    elif args.new_branch:
        sys.exit(f'git checkout -b "{args.new_branch}" && git push -u gitHub "{args.new_branch}"')
    elif args.del_branch:
        sys.exit(f'git checkout -b "{args.del_branch}" && git push -u gitHub --delete "{args.del_branch}"')

    return args
