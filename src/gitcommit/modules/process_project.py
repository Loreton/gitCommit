#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 10-07-2026 14.32.19
#

import sys; sys.dont_write_bytecode = True
from pathlib import Path

### - project modules
from pyLnLib.logger import  get_logger
from pyLnLib.colors import  get_colors

# from gitcommit.modules import getGitRoot, processArgs, parseInput, gitStatus, helpCommands
from gitcommit.modules import gitStatus

logger = get_logger()
C = get_colors()




###################################################
#
###################################################
def processArgs(fCommit: bool, fPush: bool, gitRoot: str) -> tuple[list, str]:
    args=get_project_vars("input_args")
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





###################################################
# ---- update pyproject.toml ----
###################################################
def process_single_project(project_name: str, project_dir: Path|str) -> None:
    # prj_name = Path(project_dir).stem
    parent = Path(project_dir).parent

    logger.info("")
    logger.notify("="*50)
    logger.notify("project_name: %s, project_dir: %s/", project_name, project_dir)

    fCommit, fPush = gitStatus(project_name=project_name, project_dir=project_dir)
    return

    commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=project_dir)
    executeCommit(gitROOT=project_dir, commandsList=commandsList, commit_description=commit_description, fExecute=False)
    choice=keyboardPrompt(text_msg="enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
    if choice[0] == "--go":
        '''devo di nuovo processare, prima di procedere,
            perché alcuni file potrebbero subire modifiche
            (CHANGELOG.MD o pyproject.toml, o altri)'''

        commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=project_dir)
        executeCommit(gitROOT=project_dir, commandsList=commandsList, commit_description=commit_description, fExecute=True)

    # else:
    #     logger.notify(f"{C.yellowH}{prj_name}: {C.yellow} 🚀 nothing to do!",  color=C.green)
