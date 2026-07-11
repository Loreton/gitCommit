#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 17.51.25
#

import sys; sys.dont_write_bytecode = True
from pathlib import Path

### - project modules
from pyLnLib.logger import  get_logger
from pyLnLib.colors import  get_colors
from pyLnLib.context import  get_project_vars
from pyLnLib.lndict import  lnDict

# from gitcommit.modules import getGitRoot, processArgs, parseInput, gitStatus, helpCommands
from gitcommit.modules import get_last_tag, gitStatus

logger = get_logger()
C = get_colors()







def check_arg_scan(project: lnDict) -> None:
    args = get_project_vars("input_args")
    # project_path = project["path"]
    flags = project["flags"]

    if args.scan:
        from datetime import datetime
        if flags.commit:
            now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            flags.commit_description = f"update on {now}" ### force


def check_version(project: lnDict) -> None:
    args = get_project_vars("input_args")
    flags = project["flags"]

    if args.version:
        """ ignoriamo la versione e facciamo solo commit e push di tutto quello che c'è da fare... """
        flags.last_tag = get_last_tag(gitRoot=project.path)
        flags.new_tag = flags.last_tag
        flags.fNewVersion, flags.version = processVersion(flags.last_tag)
        flags.new_tag = f"v{flags.version}"
        # args.description=f"{args.description} (Release {flags.version})"
        flags.commit_description=f"{args.description} (Release {flags.version})"

###################################################
# ---- update pyproject.toml ----
###################################################
def process_project(project: lnDict) -> None:
    project_path = project["path"]
    flags = project["flags"]

    print()
    logger.info("-"*50)
    logger.info(f"project_name: {C.yellow}%s{C.reset}", project.name)
    logger.info("project_dir: %s/",project_path)


    gitStatus(project)
    if flags.commit or flags.push:
        logger.notify("commit: %s - Push: %s", flags.commit, flags.push)
        check_arg_scan(project)
        check_version(project)




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
