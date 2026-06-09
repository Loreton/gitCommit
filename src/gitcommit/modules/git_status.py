#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 09-06-2026 18.51.14
#

import sys; sys.dont_write_bytecode = True
from datetime import datetime
from pathlib import Path

import json

### - project modules
import pyLnLib as lnLib
# from pyLnLib import  gVars as gv, Color as C

# gv     = lnLib.gVars


######################################################
# read git status and return:
#   True:  something to commit
#   False: nothing to commit
######################################################
# def gitStatus(path: str, logger=lnLib.gVars.logger, show_log: bool=True):
def gitStatus(git_dir: str):
    C      = lnLib.Color
    logger = lnLib.gVars.logger
    ###- read git status
    # logger = lnLib.DummyPrintLogger() if not show_log else gv.logger
    rcode, stdout, stderr = lnLib.lnRun("git status", cwd=git_dir, fExecute=True, toLogger=logger, stacklevel=0)
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
        logger.info("some commits must be pushed!")
        push = True

    if "nothing to commit" in stdout:
        logger.info("no changes occurred!")
        commit = False

    elif "Changes not staged for commit" in stdout or "Untracked file" in stdout or "git add" in stdout:
        logger.info(f"some changes occurred!")
        commit = True


    logger.info("commit: %s - Push: %s", commit, push)
    return commit, push






