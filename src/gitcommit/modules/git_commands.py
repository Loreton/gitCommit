#!/usr/bin/env python3
#
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
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
    rcode, stdout, stderr = lnRun(git_command, f_execute=fExecute, cwd=cwd, stacklevel=0)
    if rcode != 0:
        logger.error("runGitCommand: failed to run git command: %s", git_command)
        logger.error("error: %s", stderr, exit=True)

    return rcode, stdout.strip()





def is_git_repo(path: str) -> bool:
    """Verifica se la directory è un repository Git."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)

###################################################
#
###################################################
def get_git_root(git_root: str = None) -> str:
    rcode, stdout = _runGitCommand("git rev-parse --show-toplevel", fExecute=True, cwd=git_root)
    if rcode != 0:
        logger.error("get_git_root: path is not a git repository: %s", git_root, exit=True)

    path = stdout.strip()
    if not is_git_repo(path):
        logger.error("get_git_root: path is not a git repository: %s", path, exit=True)

    return path


###################################################
#
###################################################
def get_last_tag(git_root: str) -> str|None:
    """
    Recupera l'ultimo tag dal repository git

    Returns:
        str: L'ultimo tag trovato, None se non ci sono tag
    """
    logger.debug("Recupero ultimo tag dal repository...")

    # Esegui git describe
    _rcode, stdout, _stderr = lnRun( 'git describe --tags --abbrev=0', cwd=git_root, f_execute=True, stacklevel=0, exit_on_error=False)

    # Comando eseguito con successo e c'è output
    if _rcode == 0 and stdout:
        tag = stdout.strip()
        logger.debug(f"Ultimo tag trovato: {tag}")
        return tag

    # Nessun tag nel repository
    if _rcode != 0 and "No names found" in _stderr:
        logger.debug("Nessun tag trovato nel repository (repository senza tag)")
        return "v0.0.0"

    # Altri errori (es. non è un repository git)
    if _rcode != 0:
        logger.warning(f"Impossibile recuperare l'ultimo tag: {_stderr.strip()}")
        return None

    return None


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

    logger.info("git status output:\n%s", stdout, trim_line=True)

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
