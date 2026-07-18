#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 15.38.47
#

import sys

from pyLnLib.files.yaml_loader_class import Path; sys.dont_write_bytecode = True
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
def gitStatus(project: lnDict, logger_level: str="warning")->None:
    saved_logger_level = logger.getConsoleLoggerLevel()
    logger.setConsoleLoggerLevel(logger_level)
    flags = project["flags"]


    logger.debug("working on dir: %s", project.path, color=C.whiteH)
    rcode, stdout, stderr = lnRun("git status", cwd=project.path, fExecute=True, stacklevel=0)
    commit = True
    push = False

    if rcode:
        logger.error("project name: %s on path: %s", project.name, project.path )
        logger.error("%s", stdout)
        logger.error("%s", stderr)
        sys.exit(1)
    else:
        for line in stdout.splitlines():
            logger.debug(line, color=C.blue)

    ###- check git status output
    if "Your branch is ahead of" in stdout or 'use "git push"' in stdout:
        logger.debug("some commits must be pushed!", color=C.yellowH)
        push = True

    if "nothing to commit" in stdout:
        logger.debug("no commit necessary!")
        commit = False

    elif "Changes not staged for commit" in stdout or "Untracked file" in stdout or "git add" in stdout:
        logger.debug("some changes occurred!", color=C.yellowH)
        commit = True

    if commit or push:
        logger.debug("commit: %s - Push: %s", commit, push)
    else:
        logger.debug("no commit necessary!")

    logger.setConsoleLoggerLevel(saved_logger_level)
    flags.commit = commit
    flags.push = push
