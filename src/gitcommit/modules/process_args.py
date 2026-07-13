#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-07-2026 21.25.20
#

import sys
from webbrowser import get; sys.dont_write_bytecode = True
import re

### - project modules
from pyLnLib           import  gVars as ctx, get_logger, get_project_vars

from .get_last_tag     import  get_last_tag
from .change_log       import  generate_changelog
from .update_library   import  update_library
from .update_pyproject import  update_pyproject

logger=get_logger()
# prj=get_project_vars()




###################################################
#
###################################################
def processArgs(fCommit: bool, fPush: bool, gitRoot: str) -> tuple[list, str]:
    prjVars=get_project_vars()
    args=prjVars.input_args
    cmdList=[]

    # ----------------------------
    # - read git status
    # ----------------------------
    fNewVersion=None

    if args.scan:
        from datetime import datetime
        fPush=fCommit
        now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        # args.description=f"update on {now}" ### force
        commit_description: str =f"update on {now}" ### force

    else:
        """ ignoriamo la versione e facciamo solo commit e push di tutto quello che c'è da fare... """
        last_tag = get_last_tag(gitRoot=gitRoot)
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
