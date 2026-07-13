#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.44.48
#

# import sys
# sys.dont_write_bytecode = True
import os

### - project modules
from pyLnLib import  lnRun
from pyLnLib import  get_logger, get_colors
logger=get_logger()
C = get_colors()


def _runGitCommand(git_command: str, fExecute: bool = False, cwd: str|None = None) -> tuple[int, str]:
    rcode, stdout, stderr = lnRun( git_command, fExecute=fExecute, cwd=cwd, stacklevel=1 )
    if rcode != 0:
        logger.error("runGitCommand: failed to run git command: %s", git_command)
        logger.error("error: %s", stderr, exit=True)

    return rcode, stdout.strip()




###################################################
#
###################################################
def getGitRoot(git_root: str|None = None) -> tuple[int, str]:
    rcode, stdout = _runGitCommand("git rev-parse --show-toplevel", fExecute=True, cwd=git_root)
    return rcode, stdout.strip()


###################################################
#
###################################################
def get_last_tag(git_root: str|None = None) -> tuple[int, str]:
    rcode, stdout = _runGitCommand("git describe --tags --abbrev=0", fExecute=True, cwd=git_root)
    tag = "v0.0.0" if rcode else stdout.strip()
    return rcode, tag


def is_git_repo(path: str) -> bool:
    """Verifica se la directory è un repository Git."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


######################################################
# read git status and return:
#   True:  something to commit
#   False: nothing to commit
######################################################
def git_status(git_root: str, logger_level: str="warning")->tuple[bool, bool]:
    saved_logger_level = logger.getConsoleLoggerLevel()
    logger.setConsoleLoggerLevel(logger_level)

    _rcode, stdout = _runGitCommand("git status", cwd=git_root, fExecute=True)
    commit = True
    push = False

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
    return commit, push
