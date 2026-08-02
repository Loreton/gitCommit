#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#

from logging import warning
import sys
from webbrowser import get; sys.dont_write_bytecode = True
import re

### - project modules
from pyLnLib.logger           import get_logger
from pyLnLib.context   import ctx, lnContext

logger=get_logger()
# pvars=get_project_vars()



###################################################
# custruisce il formato della versione (MAJOR.MINOR.PATCH)
###################################################
def bump(version, level):
    major, minor, patch = map(int, version.split("."))
    if level == "patch": patch += 1
    elif level == "minor": minor += 1; patch = 0
    elif level == "major": major += 1; minor = 0; patch = 0
    return f"{major}.{minor}.{patch}"


###################################################
# ---- ---
###################################################
def validate(version):
    SEMVER_REGEX = r"^\d+\.\d+\.\d+$"
    if not re.match(SEMVER_REGEX, version):
        raise ValueError(f"Formato versione {version} non valido (MAJOR.MINOR.PATCH)")


###################################################
# return tag flag
###################################################
def version(git_prj: lnDict) ->bool:
    args=ctx.input_args



    if args.version:
        ''' è stato chiesto un upgrade di version... '''
        git_prj.new_version = args.version.lstrip("v")
        # fNewVersion = True

    elif any([args.patch, args.minor, args.major]):
        ''' è stato chiesto un upgrade di version... '''
        level = "patch" if args.patch else "minor" if args.minor else "major"
        git_prj.new_version = bump(git_prj.curr_version, level)
    else:
        ''' la versione rimane invariata'''
        git_prj.new_version = git_prj.curr_version

    validate(git_prj.new_version)
    if not git_prj.update_tag:
        git_prj.new_version = git_prj.curr_version

    # controllo della versione (escludendo il minor version)
    if git_prj.new_version[:-2] != git_prj.curr_version[:-2] or args.tag:
        set_tag = True # forziamo  tag
    else:
        set_tag = args.tag

    if set_tag:
        logger.notify("=== RELEASE TAG ===")
        logger.info("Last tag: %s", git_prj.last_tag)
        logger.info("new  tag: v%s", git_prj.new_version)
        if f"v{git_prj.new_version}" == git_prj.last_tag:
            logger.warning("Stai chiedendo il tag ma è uguale al corrente tag.")
            logger.warning("Dovresti usare --patch, --minor, --major o --version.")
            logger.error("modificare le optioni!")
            sys.exit(1)
            # set_tag = False


    return set_tag
