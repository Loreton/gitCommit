#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 13-07-2026 18.48.16
#

# import sys

# import pyLnLib
# from pyLnLib.ln_utils import flatten_and_filter; sys.dont_write_bytecode = True
# from pathlib import Path

### - project modules
import cmd

from pyLnLib.logger import  get_logger
from pyLnLib.colors import  get_colors
from pyLnLib.context import  get_project_vars
from pyLnLib.lndict import  lnDict

from .git_commands import git_status

logger = get_logger()
C = get_colors()



#===================================================
#
#===================================================
# def __check_pyLnLib(project: lnDict, logger_level: str="warning") -> str:
#     from pyLnLib import lnRun
#     rcode, stdout, stderr = lnRun("git log -1 --oneline",
#                                     fExecute=True,
#                                     cwd=project.path,
#                                     stacklevel=2
#                                 )
#     if rcode != 0:
#         logger.error(f"getGitRoot: failed to get git root: {stderr}", exit=True)
#     return  stdout.split()[0]





#===================================================
#
#===================================================
def set_description(project: lnDict) -> str:
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

    if project.python and flags.pylnlib_commit_nr and project.name != "pyLnLib":
        flags.description = f"pylnlib_commit_nr: {flags.pylnlib_commit_nr} - {flags.description}"

    return flags.description


#===================================================
# ----
#===================================================
def process_project(project: lnDict) -> bool:
    project_path = project["path"]
    flags = project["flags"]
    args = get_project_vars("input_args")
    cmd_list= project["cmd_list"]

    print()
    logger.info("-"*50)
    logger.info(f"project_name: {C.yellow}%s{C.reset}", project.name)
    logger.info("project_dir: %s/",project_path)


    flags.commit, flags.push =  git_status(git_root=project_path)

    if flags.commit:
        set_description(project)
        cmd_list.append(f'git commit -m "{flags.description}"')
        if args.push:
            cmd_list.append("git push")

    if flags.push:
        if "git push" not in cmd_list:
            cmd_list.append("git push")


    if cmd_list:
        return True
    else:
        return False
