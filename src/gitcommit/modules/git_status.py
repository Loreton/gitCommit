#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 15.38.47
#

import sys; sys.dont_write_bytecode = True
# from datetime import datetime
# from pathlib import Path

# import json

### - project modules
from pyLnLib import get_logger, get_colors, lnRun
C=get_colors()
logger=get_logger()


######################################################
# read git status and return:
#   True:  something to commit
#   False: nothing to commit
######################################################
# def gitStatus(path: str, logger=lnLib.gVars.logger, show_log: bool=True):
def gitStatus(git_dir: str):
    print()
    logger.info("working on dir: %s", git_dir, color=C.whiteH)
    rcode, stdout, stderr = lnRun("git status", cwd=git_dir, fExecute=True, stacklevel=0)
    commit = True
    push = False

    if rcode:
        print(f"\t{C.redH}ERROR! on path: {git_dir}{C.reset}")
        print(f"\t{C.redH}{stdout}{C.reset}")
        print(f"\t{C.redH}{stderr}{C.reset}")
        sys.exit(1)
    else:
        for line in stdout.splitlines():
            logger.info(line, color=C.blue)

    ###- check git status output
    if "Your branch is ahead of" in stdout or 'use "git push"' in stdout:
        logger.info("some commits must be pushed!", color=C.yellowH)
        push = True

    if "nothing to commit" in stdout:
        logger.info("no commit necessary!")
        commit = False

    elif "Changes not staged for commit" in stdout or "Untracked file" in stdout or "git add" in stdout:
        logger.info("some changes occurred!", color=C.yellowH)
        commit = True

    if commit or push:
        logger.info("commit: %s - Push: %s", commit, push)
    return commit, push
