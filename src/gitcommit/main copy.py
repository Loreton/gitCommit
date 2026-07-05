#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.54.26
#

import pdb
import sys; sys.dont_write_bytecode = True
import os

from pathlib import Path
from datetime import datetime


### - project modules
# from pyLnLib           import lnLogger,  Color as C, lnRun, gVars as gv, keyboardPrompt
from pyLnLib           import get_logger, get_colors, lnRun, gVars as ctx, keyboardPrompt
C=get_colors()
logger=get_logger()

from gitcommit.modules import getGitRoot, processArgs, parseInput, gitStatus, helpCommands


def is_git_repo(path):
    """Verifica se la directory è un repository Git."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)



def scan_repos_recursively_01(base_path: str) -> list:
    """Scansiona ricorsivamente tutte le sottodirectory per repository Git."""
    repo_list = []
    exclude_strings = {"prev", "saved", ".pio", "wkdevel", ".pyenv", "to_be_removed"}  # set = lookup più veloce

    for root, dirs, _files in os.walk(base_path):
        root_lower = root.lower()

        # Skip condizioni
        if (
            root.endswith('_') or
            root_lower.endswith('_old') or
            any(excl in root_lower for excl in exclude_strings)
        ):
            continue

        if not is_git_repo(root):
            continue

        repo_list.append(root)

        commit, push = gitStatus(git_dir=root)
        if commit or push:
            # Non scendere nei sottofolder se repo "attivo" (evita repo annidati)
            dirs.clear()

    return repo_list



#################################################################
#  SCAN_REPOS_RECURSIVELY + performante
#################################################################
def scan_repos_recursively(base_path: str) -> list:
    repo_list = []
    exclude_strings = {"prev", "saved", ".pio", "wkdevel", ".pyenv", "to_be_removed"}  # set = lookup più veloce

    for root, dirs, _files in os.walk(base_path):
        # Filtra dirs IN PLACE → enorme boost performance
        dirs[:] = [
            d for d in dirs
            if not (
                d.endswith('_') or
                d.lower().endswith('_old') or
                any(excl in d.lower() for excl in exclude_strings)
            )
        ]

        if not is_git_repo(root):
            continue

        # repo_list.append(root)

        commit, push = gitStatus(git_dir=root)
        if commit or push:
            dirs.clear()
            repo_list.append(root)

    return repo_list





#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################
def main():
    def executeCommands(fExecute: bool=False):
        for cmd in commandsList:
            lnRun(cmd, fExecute=fExecute, cwd=gitROOT, timeout=300)

    args        = parseInput()
    ctx.args     = args

    logger.setNameLength(dynamic=False, length=args.log_name_length)
    logger.setShowCaller(show_caller=args.log_show_caller)

    if args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)

    rootDirs = []
    if args.scan:
        this_top_dir = Path(os.getcwd()).resolve()
        git_repo_dir=os.path.expandvars('${ln_GIT_REPO_DIR}')
        args.changelog=False
        args.tag=False
        args.minor=False
        args.major=False
        args.patch=False
        args.version=None
        rootDirs.extend(scan_repos_recursively(str(git_repo_dir)))
        rootDirs.extend(scan_repos_recursively(str(this_top_dir)))

    else:
        rootDirs.append(Path(getGitRoot()))
        rootDirs.append(os.path.expandvars('${ln_PY_LNLIB_DIR}'))

    if not rootDirs:
        logger.warning("🚀 no directories with .git folder in subfolders found!")
        return

    print("the following projects will be committed (if necessary):")
    for _dir in rootDirs:
        print(f"\t{str(_dir)}")

    choice: list[str]=keyboardPrompt(text_msg="continue [c]", validKeys=["c"], exitKeys=["n", "x", "q", "ENTER"])
    if choice[0] != "c":
        return

    now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    for gitROOT in rootDirs:
        prj_name=Path(gitROOT).stem
        parent=Path(gitROOT).parent

        fCommit, fPush = gitStatus(git_dir=gitROOT)

        logger.info("")
        logger.notify("="*50)
        logger.notify(f"gitROOT: {parent}/{C.yellow}{prj_name}")

        # if args.scan:
        #     commit_description = f"update on {now}"
        # else:
        #     commit_description = args.description

        if fCommit:
            if args.go:
                commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                commandsList.insert(0, f"git commit -m '{commit_description}'")
                commandsList.insert(0, "git add .")
                logger.notify("=== start Command list ===")
                executeCommands(fExecute=True)

            else:
                commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                commandsList.insert(0, f"git commit -m '{commit_description}'")
                commandsList.insert(0, "git add .")
                executeCommands(fExecute=False)

                choice=keyboardPrompt(text_msg="enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
                if choice[0] == "--go":
                    args.go = True ### forcing
                    '''devo di nuovo processare, prima di procedereffettivamente,
                        perché alcuni file potrebbero essere stati modificati
                        (CHANGELOG.MD o pyproject.toml, o altri)'''
                    commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                    commandsList.insert(0, f"git commit -m '{commit_description}'")
                    commandsList.insert(0, "git add .")
                    executeCommands(fExecute=True)
                else:
                    continue

        else:
            logger.notify(f"{C.yellowH}{prj_name}: {C.yellow} 🚀 nothing to do!",  color=C.green)



if __name__ == "__main__":
    main()
