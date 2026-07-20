#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2026 14.04.01
#

from logging import warning
import sys
from webbrowser import get; sys.dont_write_bytecode = True
import re

### - project modules
from pyLnLib           import  get_logger, get_project_vars, lnDict

# from .get_last_tag     import  get_last_tag
# from gitcommit.files.changelog       import  generate_changelog
# from .update_library   import  update_library
# from .update_pyproject import  update_pyproject
# from .git_commands import git_status
logger=get_logger()
pvars=get_project_vars()



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
    args=get_project_vars("input_args")

    if args.version:
        ''' è stato chiesto un upgrade di version... '''
        git_prj.new_version = args.version.lstrip("v")
        # fNewVersion = True

    elif any([args.patch, args.minor, args.major]):
        ''' è stato chiesto un upgrade di version... '''
        level = "patch" if args.patch else "minor" if args.minor else "major"
        git_prj.new_version = bump(git_prj.last_version, level)
    else:
        ''' la versione rimane invariata'''
        git_prj.new_version = git_prj.last_version

    validate(git_prj.new_version)

    # controllo della versione (escludendo il minor version)
    if git_prj.new_version[:-2] != git_prj.last_version[:-2] or args.tag:
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
            logger.warning("L'opzione verrà ignorata!")
            set_tag = False


    return set_tag
