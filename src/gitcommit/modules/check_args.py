#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-07-2026 21.25.20
#

import sys
from webbrowser import get; sys.dont_write_bytecode = True
import re

### - project modules
from pyLnLib           import  get_logger, get_project_vars, lnDict

from .get_last_tag     import  get_last_tag
from .change_log       import  generate_changelog
from .update_library   import  update_library
from .update_pyproject import  update_pyproject
from .git_commands import git_status
logger=get_logger()
pvars=get_project_vars()



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


###################################################
#
###################################################
def processVersion(last_tag: str):
    args=get_project_vars("input_args")

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



###################################################
#
###################################################
def check_args(git_prj: lnDict) -> None:
    args=get_project_vars("input_args")
    # gitRoot=git_prj.path

    # ----------------------------
    # - read git status
    # ----------------------------
    git_prj.commit, git_prj.push = git_status(git_root=git_prj.path)
    fNewVersion=None

    import pdb; pdb.set_trace();  # by Loreto
    if args.scan:
        from datetime import datetime
        git_prj.push = git_prj.commit
        now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        # args.description=f"update on {now}" ### force
        commit_description: str =f"update on {now}" ### force

    else:
        """ ignoriamo la versione e facciamo solo commit e push di tutto quello che c'è da fare... """
        last_tag = get_last_tag(gitRoot=git_prj.path)
        new_tag = last_tag
        fNewVersion, version = processVersion(last_tag)
        new_tag = f"v{version}"
        # args.description=f"{args.description} (Release {version})"
        commit_description=f"{args.description} (Release {version})"

        # ----------------------------
        # - changelog
        # ----------------------------
        if args.changelog:
            updated_changelog = generate_changelog(version=version, fExecute=args.go, gitRoot=gitRoot)
            if updated_changelog and fCommit:
                cmdList.append("git add CHANGELOG.md")


        # ----------------------------
        # - tag
        # ----------------------------
        if args.tag:
            if new_tag == last_tag:
                logger.warning("Stai chiedendo il tag ma non è stato richiesto alcun incremento per la versione.")
                logger.warning("L'opzione verrà ignorata!")
                args.tag = False
            else:
                # ---- update library.json ----
                updated = update_library(version=version, fExecute=args.go, gitRoot=gitRoot)
                if updated and fCommit:
                    cmdList.append("git add library.json")

                updated = update_pyproject(new_version=version, fExecute=args.go, gitRoot=gitRoot)
                if updated and fCommit:
                    cmdList.append("git add pyproject.toml")

                cmd = f'git tag -a "{new_tag}"'
                if fNewVersion: cmd = f'{cmd} -m "Release {version}"'
                cmdList.append(cmd)

            logger.notify("=== RELEASE PLAN ===")
            logger.info("Last tag: %s", last_tag)
            logger.info("new  tag: %s", new_tag)

    # ----------------------------
    # - push
    # ----------------------------
    if args.push or fPush:
        cmdList.append("git push")
        if args.tag:
            cmdList.append("git push --tags")



    # ----------------------------
    # - commit ----
    # ----------------------------
    # if fCommit:
        # cmd = f'git commit -m "{args.description}"'
        # cmd = f'git commit -m "{commit_description}"'
        # cmdList.insert(0, cmd)
        # cmdList.insert(0, "git add .")


    return cmdList, commit_description
