#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2026 14.04.01
#

import sys
from webbrowser import get; sys.dont_write_bytecode = True
import re

### - project modules
from pyLnLib           import  get_logger, get_project_vars, lnDict

# from .get_last_tag     import  get_last_tag
from gitcommit.files.changelog       import  generate_changelog
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
#
###################################################
def check_version(git_prj: lnDict):
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

    if git_prj.new_version != git_prj.last_version:
        args.changelog = True

    return






###################################################
#
###################################################
def check_args(git_prj: lnDict) -> tuple[list[str], str]:
    args=get_project_vars("input_args")

    # ----------------------------
    # - read git status
    # ----------------------------
    # git_prj.commit, git_prj.push = git_status(git_root=git_prj.path)
    fNewVersion=None
    cmdList = []
    commit_description = str()

    if args.scan:
        from datetime import datetime
        git_prj.push = git_prj.commit
        now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        commit_description =f"update on {now}" ### force

    else:
        """ ignoriamo la versione e facciamo solo commit e push di tutto quello che c'è da fare... """
        # last_tag = get_last_tag(gitRoot=git_prj.path)
        # new_tag = last_tag
        git_prj.new_version = git_prj.last_version
        processVersion(args=args, last_version=git_prj.last_version)
        if git_prj.new_version != git_prj.last_version:
            args.changelog = True
        # new_tag = f"v{version}"
        # commit_description=f"{args.description} (Release {version})"

        # ----------------------------
        # - changelog
        # ----------------------------
        if args.changelog:
            updated_changelog = generate_changelog(version=version, fExecute=args.go, gitRoot=git_prj.path)
            if updated_changelog and git_prj.commit:
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
                updated = update_library(version=version, fExecute=args.go, gitRoot=git_prj.path)
                if updated and git_prj.commit:
                    cmdList.append("git add library.json")

                updated = update_pyproject(new_version=version, fExecute=args.go, gitRoot=git_prj.path)
                if updated and git_prj.commit:
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
    if args.push or git_prj.push:
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
