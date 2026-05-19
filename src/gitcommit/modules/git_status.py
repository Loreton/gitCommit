#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 18-05-2026 10.02.55
#

import sys; sys.dont_write_bytecode = True
from datetime import datetime
from pathlib import Path

import json

### - project modules
from pyLnLib import  gVars as gv, lnRun, Color as C, DummyPrintLogger

###################################################
#
###################################################
# def getGitRoot():
#     rcode, stdout, stderr = lnRun(
#         "git rev-parse --show-toplevel",
#         fExecute=True,
#         toLogger=gv.logger,
#         stacklevel=2
#     )
#     return stdout.strip()


# ###################################################
# #
# ###################################################
# def get_last_tag(gitRoot: str):
#     rcode, stdout, stderr = lnRun("git describe --tags --abbrev=0",
#                                     fExecute=True,
#                                     cwd=gitRoot,
#                                     toLogger=gv.logger,
#                                     stacklevel=2
#                                 )

#     tag = stdout.strip()

#     return tag if tag else "v0.0.0"


######################################################
# read git status and return:
#   True:  something to commit
#   False: nothing to commit
######################################################
def gitStatus(path: str, show_log: bool=True, logger=gv.logger):
    ###- read git status
    # logger = DummyPrintLogger() if no_log else gv.logger
    logger = DummyPrintLogger() if not show_log else gv.logger
    rcode, stdout, stderr = lnRun("git status", cwd=path, fExecute=True, toLogger=logger, stacklevel=0)
    commit = True
    push = False

    if rcode:
        print(f"\t{C.redH}ERROR! on path: {path}{C.reset}")
        print(f"\t{C.redH}{stdout}{C.reset}")
        print(f"\t{C.redH}{stderr}{C.reset}")
        sys.exit(1)

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






