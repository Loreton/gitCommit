#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-07-2026 21.25.20
#

import sys
from webbrowser import get

from pyLnLib.lndict.ln_dict_class import lnDict; sys.dont_write_bytecode = True
import re

### - project modules
from pyLnLib           import  gVars as ctx, get_logger, get_project_vars, lnDict

from .get_last_tag     import  get_last_tag
# from .change_log       import  generate_changelog
# from .update_library   import  update_library
# from .update_pyproject import  update_pyproject

logger=get_logger()
# prj=get_project_vars()


###################################################
#
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


#===================================================
#
#===================================================
def check_version_XXX(project: lnDict) -> None:
    args = get_project_vars("input_args")
    flags = project["flags"]

    if args.version:
        """ ignoriamo la versione e facciamo solo commit e push di tutto quello che c'è da fare... """
        flags.last_tag = get_last_tag(gitRoot=project.path)
        flags.new_tag = flags.last_tag
        flags.fNewVersion, flags.version = checkVersion(flags.last_tag)
        flags.new_tag = f"v{flags.version}"
        # args.description=f"{args.description} (Release {flags.version})"
        flags.commit_description=f"{args.description} (Release {flags.version})"



###################################################
#
###################################################
def get_version(project: lnDict):
    args = get_project_vars("input_args")

    # ----------------------------
    # - determina versione
    # ----------------------------
    if args.version:
        ''' è stato chiesto un upgrade di version... '''
        version = args.version.lstrip("v")
        fNewVersion = True

    elif any([args.patch, args.minor, args.major]):
        ''' è stato chiesto un upgrade di version... '''
        level = "patch" if args.patch else "minor" if args.minor else "major"
        version = bump(last_tag.lstrip('v'), level)
        fNewVersion = True
    else:
        ''' la versione rimane invariata'''
        version = last_tag.lstrip('v')
        fNewVersion = False

    if fNewVersion:
        args.tag = True
        args.changelog = True

    validate(version)

    return fNewVersion, version
