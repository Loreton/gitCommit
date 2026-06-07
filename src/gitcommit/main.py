#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-06-2026 20.04.41
#

import sys; sys.dont_write_bytecode = True
import os

from pathlib import Path


### - project modules
from pyLnLib           import lnLogger,  Color as C, lnRun, gVars as gv, keyboardPrompt
from gitcommit.modules           import getGitRoot, processArgs, parseInput, gitStatus, helpCommands





def is_git_repo(path):
    """Verifica se la directory è un repository Git."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)



def scan_repos_recursively_01(base_path: str) -> list:
    """Scansiona ricorsivamente tutte le sottodirectory per repository Git."""
    repo_list = []
    exclude_strings = {"prev", "saved", ".pio", "wkdevel", ".pyenv", "to_be_removed"}  # set = lookup più veloce

    for root, dirs, files in os.walk(base_path):
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

        commit, push = gitStatus(root, show_log=True)
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

    for root, dirs, files in os.walk(base_path):
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

        repo_list.append(root)

        commit, push = gitStatus(root, show_log=True)
        if commit or push:
            dirs.clear()

    return repo_list

#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################
def main():
    def executeCommands(fExecute: bool=False):
        for cmd in commandsList:
            lnRun(cmd, fExecute=fExecute, cwd=gitROOT, toLogger=gv.logger)

    # gv.logger   = lnLogger(name = 'Loreto', level = "info", logging_dir = '/tmp' )
    gv.logger=lnLogger(name="git_commit",
                            console_logger_level="info", ### --- default
                            file_logger_level="warning",
                            logging_dir=None, # no filehandler
                            threads=False)
    args        = parseInput()
    gv.args     = args
    gv.fExecute = args.go

    gv.logger.setNameLength(dynamic=False, length=args.log_name_length)
    gv.logger.setShowCaller(show_caller=args.log_show_caller)
    gv.logger.setLinenoLength(len=4)

    if args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)

    rootDirs = []
    if args.scan:
        top_dir = Path(os.getcwd()).resolve()
        args.changelog=False
        args.tag=False
        args.minor=False
        args.major=False
        args.patch=False
        args.version=None
        rootDirs = scan_repos_recursively(top_dir)
    else:
        rootDirs.append(Path(getGitRoot()))



    if not rootDirs:
        gv.logger.warning("🚀 no directories with .git folder in subfolders found!")
        return

    for gitROOT in rootDirs:
        dirname=Path(gitROOT).stem
        parent=Path(gitROOT).parent

        fCommit, fPush = gitStatus(gitROOT, show_log=True)

        gv.logger.info("")
        gv.logger.notify("="*50)
        gv.logger.notify(f"gitROOT: {parent}/{C.yellow}{dirname}")

        if fCommit:
            if args.go:
                commandsList = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                gv.logger.notify("=== start Command list ===")
                executeCommands(fExecute=True)

            else:
                commandsList = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                executeCommands(fExecute=False)

                choice=keyboardPrompt(text_msg="enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
                if choice.startswith("--go"):
                    ### devo rifare il processo perché alcuni file potrebbero andare modificati
                    commandsList = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                    executeCommands(fExecute=True)
                else:
                    continue

                # print(f"\n\t{gv.colors.cyanH}[dry-run] --go to execute{gv.colors.reset}\n")
        else:
            gv.logger.notify(f"{C.yellowH}{dirname}: {C.yellow} 🚀 nothing to do!",  color=C.green)






if __name__ == "__main__":
    main()
