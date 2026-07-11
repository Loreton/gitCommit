#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 11-07-2026 15.45.14
#

import sys

sys.dont_write_bytecode = True
import os
from pathlib import Path
import yaml

     ### - project modules
from     pyLnLib.context   import gVars as ctx, get_project_vars
from     pyLnLib.colors    import get_colors
from     pyLnLib.logger    import get_logger, init_logger
from     pyLnLib.system    import lnRun
from     pyLnLib    import keyboardPrompt
from     pyLnLib.files     import zipDir, get_yaml_engine
from     pyLnLib.lndict     import lnDict

C=get_colors()
prjVars=get_project_vars()
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
        # x=lnDict
        commit, push = gitStatus(git_dir=root)
        if commit or push:
            # Non scendere nei sottofolder se repo "attivo" (evita repo annidati)
            dirs.clear()

    return repo_list



#################################################################
#  SCAN_REPOS_RECURSIVELY + performante
#################################################################
def scan_repos_recursively(base_path: str|Path) -> list:
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

        repo_list.append(root)

        commit, push = gitStatus(git_dir=root)
        if commit or push:
            dirs.clear()
            repo_list.append(root)

    return repo_list


def confirm_dirs(rootDirs: list[str]) -> bool:
    if len(rootDirs) > 1:
        print("the following projects will be committed!:")
        for _dir in rootDirs:
            print(f"\t{C.yellow}{str(_dir)}{C.reset}")

        choice: list[str]=keyboardPrompt(text_msg="continue [c]", validKeys=["c"], exitKeys=["n", "x", "q", "ENTER"])
        if choice[0] == "c":
            return True
        else:
            return False
    else:
        logger.warning("🚀 no directories, with .git folder, in subfolders found!")
        return False


def executeCommit(gitROOT: str, commandsList: list[str], commit_description: str|None=None, fExecute: bool=False):
    commandsList.insert(0, f"git commit -m '{commit_description}'")
    commandsList.insert(0, "git add .")
    logger.notify("=== start Command list ===")
    for cmd in commandsList:
        lnRun(cmd, fExecute=fExecute, cwd=gitROOT, timeout=300)


def process_scanned_dirs(rootDirs: list[str]):
    for gitROOT in rootDirs:
        commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
        executeCommit(gitROOT=gitROOT, commandsList=commandsList, commit_description=commit_description, fExecute=True)




#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################
def main():
    #### 1. logger initializzation
    logger=init_logger(logger_name="gitCommit", test=False)
    #### 2. read static project list file
    yaml_engine=get_yaml_engine(search_paths=[ctx.get_conf_dir()], recursive=True)
    config_file = ctx.get_conf_dir() / "projects_list.yaml"
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))

    #### 3. initialize project variables
    prjVars.update(config_data)

    #### 4. processo input arguments....
    args = parseInput()
    prjVars["input_args"]=vars(args) # include args in project_vars

    #### 4a. update logger as requested by input arguments
    logger.setNameLength(dynamic=False, length=args.log_name_length)
    logger.setShowCaller(show_caller=args.log_show_caller)

    # prepariamo i percorsi importanti
    prj_top_dir = Path.cwd().resolve()
    prj_repo_dir = Path(getGitRoot())


    # print project variables if requested
    if args.vars:
        print(prjVars)
        sys.exit(0)

    # list commands if requested
    if args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)

    # create pyLnLib.zip if requested
    if args.ziplib:
        pyLnLib_path = prjVars.root_dirs.pyLnLib_dir /  "src/pyLnLib"
        zipDir(source_dir=pyLnLib_path, output_zip=prj_top_dir / "pyLnLib.zip")

    args = get_project_vars("input_args")
    #### 5. prepare rootDirs for searching git projects
    rootDirs = []
    if args.scan:
        for prj_name, prj_dir in prjVars.git_project_dirs.items():
            import pdb; pdb.set_trace();  # by Loreto
            process_single_project(project_dir=prj_dir)

        """ scan for git projects recursively in the current directory and in the git repo directory"""
        rootDirs.extend(scan_repos_recursively(prj_top_dir))
        rootDirs.extend(scan_repos_recursively(git_repo_dir))
        if confirm_dirs(rootDirs):
            process_scanned_dirs(rootDirs)
        else:
            sys.exit(0)
    else:
        """ use the current directory and the pyLnLib directory as the root directories"""
        rootDirs.append(pyLnLib_path)
        rootDirs.append(prj_repo_dir)
        if confirm_dirs(rootDirs):
            process_this_project(rootDirs)
        else:
            sys.exit(0)



    sys.exit("processo completato!")


#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################
def main_prev():
    #### 1. logger initializzation
    logger=init_logger(logger_name="gitCommit", test=False)

    if config_dir := ctx.get_conf_dir() is None:
        logger.error("config_dir is None")
        return

    config_file = config_dir / "projects_list.yaml"
    if not config_file.exists():
        logger.error(f"config_file {config_file} does not exist")
        return


    config_str: dict = yaml.load(config_file, Loader=yaml.FullLoader)
    config = lnDict(data=config_str)
    import pdb; pdb.set_trace(); # by Loreto

    #### 2. initialize project variables
    prjVars.update(loadJsonVarsStruct())

    #### 3. processo input arguments....
    args = parseInput()
    prjVars["input_args"]=vars(args) # include args in project_vars

    #### 4. update logger as requested by input arguments
    logger.setNameLength(dynamic=False, length=args.log_name_length)
    logger.setShowCaller(show_caller=args.log_show_caller)

    # prepariamo i percorsi importanti
    pyLnLib_path = Path(os.path.expandvars('${ln_PY_LNLIB_DIR}'))
    prj_top_dir = Path.cwd().resolve()
    prj_repo_dir = Path(getGitRoot())
    git_repo_dir= Path(os.path.expandvars('${ln_GIT_REPO_DIR}'))

    # create pyLnLib.zip if requested
    if args.ziplib:
        zipDir(source_dir=pyLnLib_path / "src/pyLnLib", output_zip=prj_top_dir / "pyLnLib.zip")

    # list commands if requested
    if args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)

    #### 4. prepare rootDirs for searching git projects
    rootDirs = []
    if args.scan:
        """ scan for git projects recursively in the current directory and in the git repo directory"""
        rootDirs.extend(scan_repos_recursively(prj_top_dir))
        rootDirs.extend(scan_repos_recursively(git_repo_dir))
        if confirm_dirs(rootDirs):
            process_scanned_dirs(rootDirs)
        else:
            sys.exit(0)
    else:
        """ use the current directory and the pyLnLib directory as the root directories"""
        rootDirs.append(pyLnLib_path)
        rootDirs.append(prj_repo_dir)
        if confirm_dirs(rootDirs):
            process_this_project(rootDirs)
        else:
            sys.exit(0)




    import pdb; pdb.set_trace();  # by Loreto
    # now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    primary_project_description: str|None = None
    primary_project_name: str|None = None





    for i, gitROOT in enumerate(rootDirs, 1):
        prj_name=Path(gitROOT).stem
        parent=Path(gitROOT).parent

        fCommit, fPush = gitStatus(git_dir=gitROOT)




    for i, gitROOT in enumerate(rootDirs, 1):
        prj_name=Path(gitROOT).stem
        parent=Path(gitROOT).parent

        fCommit, fPush = gitStatus(git_dir=gitROOT)

        logger.info("")
        logger.notify("="*50)
        logger.notify(f"gitROOT: {parent}/{C.yellow}{prj_name}")

        if not args.scan:
            if prj_name == 'pyLnLib':
                commit_description = f"{primary_project_name}: {primary_project_description}"

        if fCommit:
            if args.go:
                commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                executeCommit(gitROOT=gitROOT, commandsList=commandsList, commit_description=commit_description, fExecute=True)

            else:
                commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                executeCommit(gitROOT=gitROOT, commandsList=commandsList, commit_description=commit_description, fExecute=False)
                choice=keyboardPrompt(text_msg="enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
                if choice[0] == "--go":
                    '''devo di nuovo processare, prima di procedereffettivamente,
                        perché alcuni file potrebbero essere stati modificati
                        (CHANGELOG.MD o pyproject.toml, o altri)'''

                    commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
                    executeCommit(gitROOT=gitROOT, commandsList=commandsList, commit_description=commit_description, fExecute=True)

        else:
            logger.notify(f"{C.yellowH}{prj_name}: {C.yellow} 🚀 nothing to do!",  color=C.green)

        if i == 1:
            primary_project_name = prj_name
            primary_project_description = commit_description


if __name__ == "__main__":
    main()
