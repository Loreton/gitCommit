#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 12-07-2026 21.26.00
#

# import sys

# import pyLnLib
# from pyLnLib.ln_utils import flatten_and_filter; sys.dont_write_bytecode = True
# from pathlib import Path

### - project modules
from pyLnLib.logger import  get_logger
from pyLnLib.colors import  get_colors
from pyLnLib.context import  get_project_vars
from pyLnLib.lndict import  lnDict

# from gitcommit.modules import getGitRoot, processArgs, parseInput, gitStatus, helpCommands
# from gitcommit.modules import get_last_tag, gitStatus, get_version
# from gitcommit.modules import process_pyLnLib
from .git_commands import git_status
# from gitcommit.modules.git_commands import git_status

logger = get_logger()
C = get_colors()



#===================================================
#
#===================================================
def check_pyLnLib(project: lnDict, logger_level: str="warning") -> str:
    from pyLnLib import lnRun
    rcode, stdout, stderr = lnRun("git log -1 --oneline",
                                    fExecute=True,
                                    cwd=project.path,
                                    stacklevel=2
                                )
    if rcode != 0:
        logger.error(f"getGitRoot: failed to get git root: {stderr}", exit=True)
    return  stdout.split()[0]





#===================================================
#
#===================================================
def set_description(project: lnDict) -> None:
    args = get_project_vars("input_args")
    # project_path = project["path"]
    flags = project["flags"]

    if args.scan:
        from datetime import datetime
        if flags.commit:
            now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            flags.commit_description = f"update on {now}" ### force
    else:
        flags.description = args.description




#===================================================
# ----
#===================================================
def process_project(project: lnDict) -> bool:
    retval: bool = False
    project_path = project["path"]
    flags = project["flags"]

    print()
    logger.info("-"*50)
    logger.info(f"project_name: {C.yellow}%s{C.reset}", project.name)
    logger.info("project_dir: %s/",project_path)


    flags.commit, flags.push =  git_status(git_root=project_path)
    if flags.commit or flags.push:
        logger.notify("commit: %s - Push: %s", flags.commit, flags.push)
        set_description(project)
        # get_version(project)
        retval = True

    if project.name == 'pyLnLib':
        flags.commit_nr = check_pyLnLib(project)
        retval = True  # per pyLnLib torniamo sempre True

    return retval



    # if args.version:
    #     commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=project_dir)
    #     executeCommit(gitROOT=project_dir, commandsList=commandsList, commit_description=commit_description, fExecute=False)
    #     choice=keyboardPrompt(text_msg="enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
    #     if choice[0] == "--go":
    #         '''devo di nuovo processare, prima di procedere,
    #             perché alcuni file potrebbero subire modifiche
    #             (CHANGELOG.MD o pyproject.toml, o altri)'''

    #         commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=project_dir)
    #         executeCommit(gitROOT=project_dir, commandsList=commandsList, commit_description=commit_description, fExecute=True)

        # else:
        #     logger.notify(f"{C.yellowH}{prj_name}: {C.yellow} 🚀 nothing to do!",  color=C.green)
