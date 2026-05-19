#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 18-05-2026 18.26.41
#

import sys; sys.dont_write_bytecode = True
import argparse


### - project modules
from pyLnLib import   Color as C

# ##################################################
# # parseInput
# ##################################################
def parseInput():
    from datetime import datetime
    now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    parser = argparse.ArgumentParser(description=f"Release tool {C.whiteH}{sys.argv[0]}{C.reset}")

    action_opt=parser.add_argument_group(f'{C.white} --------- action options{C.reset}')
    action_opt.add_argument("description", metavar='', nargs="?", default=f"update on {now}", type=str, help="Description")
    # action_opt.add_argument("description", metavar='', nargs="?", default=None, type=str, help="Description")
    action_opt.add_argument("--tag", action="store_true")
    action_opt.add_argument("--push", action="store_true")
    action_opt.add_argument("--changelog", action="store_true", help="Aggiorna CHANGELOG.md")
    action_opt.add_argument("--status", action="store_true", help="Display git status")
    action_opt.add_argument("--scan", action="store_true", help="scan for git repositories in all subforders")
    # action_opt.add_argument("--root-dir", metavar='', required=False, default=None, type=str, help="root dir from which scan for git repositories.")

    commands_opt=parser.add_argument_group(f'{C.white} --------- git commands{C.reset}')
    commands_opt.add_argument("--new-branch",  metavar='', default=None, type=str, help="Branch name")
    commands_opt.add_argument("--del-branch", action="store_true", help="""BR='old_branch' && git branch -d ${BR} && git push gitHub --delete ${BR}""")
    commands_opt.add_argument("--list-commands", action="store_true", help="list of some useful commands.")

    group=parser.add_argument_group(f'{C.white} --------- release options{C.reset}')
    release=group.add_mutually_exclusive_group(required=False)
    release.add_argument("--major", action="store_true", help="increments X._._")
    release.add_argument("--minor", action="store_true", help="increments _.X._")
    release.add_argument("--patch", action="store_true", help="increments _._.X")
    release.add_argument("--version", metavar='', default=None, type=str, help="Versione manuale (es 1.2.3)")

    execution_opt=parser.add_argument_group(f'{C.white} --------- execution options{C.reset}')
    execution_opt.add_argument("--go", action="store_true", help="Esegui realmente i comandi")
    execution_opt.add_argument("--log-name-length", type=int, default=0, help="module name max length")
    execution_opt.add_argument("--log-show-caller", action="store_true", help="show also caller name")
    execution_opt.add_argument("--display-args", action="store_true", help="Display arguments")
    execution_opt.add_argument("--edit", action="store_true", help="Edit this script")

    args = parser.parse_args()


    # if args.scan:
    #     args.tag = False
    #     args.push = True
    #     args.changelog = False
    #     args.major = False
    #     args.minor = False
    #     args.patch = False
    #     args.version = None


    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('\tinput arguments: {json_data}'.format(**locals()))
        sys.exit(0)



    if args.new_branch:
        command = f'git checkout -b "{args.new_branch}" && git push -u gitHub "{args.new_branch}"'
        print(command)
        # run(command, args.go, fVerbose=True)
        sys.exit(0)

    return args


