#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 13-07-2026 11.29.51
#

from inspect import stack
import sys

from gitcommit.modules.git_commands import git_status

sys.dont_write_bytecode = True
import os
from pathlib import Path
# import yaml

     ### - project modules
from     pyLnLib.context   import gVars as ctx, get_project_vars
from     pyLnLib.colors    import get_colors
from     pyLnLib.logger    import get_logger, init_logger
from     pyLnLib.system    import lnRun
from     pyLnLib    import keyboardPrompt
from     pyLnLib.files     import zipDir, get_yaml_engine
from     pyLnLib.lndict     import lnDict

C=get_colors()
pVars: lnDict=get_project_vars()
logger=get_logger()

# from gitcommit.modules import getGitRoot, processArgs, parseInput, gitStatus, helpCommands
from gitcommit.modules import parseInput, process_project, getGitRoot


def is_git_repo(path):
    """Verifica se la directory è un repository Git."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


def commit_project(project: lnDict) -> None:
    cmd_list: list[str] = []
    flags = project.flags
    args = pVars["input_args"]

    if not any([flags.commit, flags.push]):
        return True


    if flags.commit:
        cmd_list.append("git add .")
        cmd_list.append(f'git commit -m \"{flags.description}\"')
        if args.push:
            cmd_list.append("git push")

    if flags.push:
        if "git push" not in cmd_list:
            cmd_list.append("git push")

    # display command list
    print()
    logger.info(f"- {C.white}%s [commit->%s push->%s]", project.name, flags.commit, flags.push)
    for cmd in cmd_list:
        logger.info(cmd, color=C.magentaH)

    # prompt per esecuzione comandi
    choice=keyboardPrompt(text_msg=f"project: {project.name} -  enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
    if choice[0] == "--go":
        _fExecute = True ### forcing
        '''devo di nuovo processare, prima di procedereffettivamente,
            perché alcuni file potrebbero essere stati modificati
            (CHANGELOG.MD o pyproject.toml, o altri)'''

    # Esecuzione dei comandi
    for cmd in cmd_list:
        lnRun(cmd, fExecute=False, cwd=project.path, timeout=300, logger_level="info", stacklevel=1)
    logger.notify(f"{C.yellowH}{project.name}: {C.yellow} 🚀 commit/push done!",  color=C.green)
    # return True



#===================================================
#
#===================================================
def check_pyLnLib(project: lnDict, logger_level: str="warning") -> str:
    rcode, stdout, stderr = lnRun("git log -1 --oneline", fExecute=True, cwd=project.path, stacklevel=2 )
    if rcode != 0:
        logger.error(f"getGitRoot: failed to get git root: {stderr}", exit=True)
    return  stdout.split()[0]




#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################
def main():
    ctx.set_project_name("gitCommit")

    #### 1. logger initializzation
    logger=init_logger(logger_name="gitCommit", test=False)

    #### 2. read static project list file
    yaml_engine=get_yaml_engine(search_paths=[ctx.get_conf_dir()], recursive=True)
    config_file = ctx.get_conf_dir() / "projects_list.yaml"
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))

    #### 3. initialize project variables
    pVars.update(config_data)

    #### 4. processo input arguments....
    args = parseInput()
    pVars["input_args"]=vars(args) # include args in project_vars
    pVars.save_yaml(filepath=ctx.get_log_dir() / "project_vars.yaml", title="project_vars", indent=4)


    #### 4a. update logger as requested by input arguments
    logger.setNameLength(dynamic=False, length=args.log_name_length)
    logger.setShowCaller(show_caller=args.log_show_caller)

    _rcode, prj_top_dir = getGitRoot(os.path.curdir)
    prj_top_dir=Path(prj_top_dir)



    # print project variables if requested
    if args.vars:
        print(pVars)
        sys.exit(0)

    # list commands if requested
    if args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)

    # create pyLnLib.zip if requested
    if args.ziplib:
        pyLnLib_path = pVars.root_dirs.pyLnLib_dir /  "src/pyLnLib"
        zipDir(source_dir=pyLnLib_path, output_zip=prj_top_dir / "pyLnLib.zip")


    ### -----------------------------
    ### - crea una list per contenere i nomi dei progetti da processare
    ### -----------------------------
    projects_list: list[str] = [] # lista dei nomi dei progetti da processare
    if args.scan:
        projects_list= pVars.git_project_dirs.keys()
    else:
        projects_list = ['pyLnLib', prj_top_dir.name]

    projectsToProcess = lnDict()
    pylnlib_commit_nr = check_pyLnLib(pVars.git_project_dirs["pyLnLib"])
    import pdb; pdb.set_trace();  # by Loreto
    ### -----------------------------
    ### - - prepara un dict per contenere i progetti da fare commit/push
    ### - - tutti i flag dello stato saranno modificati a dovere
    ### - - salva su file, per analisi, i progetti da fare commit/push
    ### - - pyLnLib comunque compare....
    ### -----------------------------
    for prj_name in projects_list[:]:
        git_project = pVars.git_project_dirs[prj_name]
        git_project["name"] = prj_name
        git_project["cmd_list"] = []
        if git_project.python:
            git_project["flags.pylnlib_commit_nr"] = pylnlib_commit_nr
        if process_project(project=git_project):
            projectsToProcess[prj_name] = git_project

    projectsToProcess.save_yaml(filepath=ctx.get_log_dir() / "project_vars_final.yaml", title="projects_to_be_committed", indent=4)

    for prj_name in projectsToProcess.keys():
        git_project = projectsToProcess[prj_name]
        if git_project.cmd_list:
            commit_project(project=git_project)
            #     logger.notify(f"{C.yellowH}{prj_name}: {C.yellow} 🚀 commit/push done!",  color=C.green)
            # else:
            #     logger.notify(f"{C.yellowH}{prj_name}: {C.yellow} 🚀 commit/push failed!",  color=C.red)




    sys.exit("processo completato!")


#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################
# def main_prev():
#     #### 1. logger initializzation
#     logger=init_logger(logger_name="gitCommit", test=False)

#     if config_dir := ctx.get_conf_dir() is None:
#         logger.error("config_dir is None")
#         return

#     config_file = config_dir / "projects_list.yaml"
#     if not config_file.exists():
#         logger.error(f"config_file {config_file} does not exist")
#         return


#     config_str: dict = yaml.load(config_file, Loader=yaml.FullLoader)
#     config = lnDict(data=config_str)
#     import pdb; pdb.set_trace(); # by Loreto

#     #### 2. initialize project variables
#     pVars.update(loadJsonVarsStruct())

#     #### 3. processo input arguments....
#     args = parseInput()
#     pVars["input_args"]=vars(args) # include args in project_vars
#     import pdb; pdb.set_trace();  # by Loreto
#     #### 4. update logger as requested by input arguments
#     logger.setNameLength(dynamic=False, length=args.log_name_length)
#     logger.setShowCaller(show_caller=args.log_show_caller)

#     # prepariamo i percorsi importanti
#     pyLnLib_path = Path(os.path.expandvars('${ln_PY_LNLIB_DIR}'))
#     prj_top_dir = Path.cwd().resolve()
#     prj_repo_dir = Path(getGitRoot())
#     git_repo_dir= Path(os.path.expandvars('${ln_GIT_REPO_DIR}'))

#     # create pyLnLib.zip if requested
#     if args.ziplib:
#         zipDir(source_dir=pyLnLib_path / "src/pyLnLib", output_zip=prj_top_dir / "pyLnLib.zip")

#     # list commands if requested
#     if args.list_commands:
#         commands = helpCommands()
#         print(f"{C.green}{commands}{C.reset}")
#         sys.exit(0)

#     #### 4. prepare rootDirs for searching git projects
#     rootDirs = []
#     if args.scan:
#         """ scan for git projects recursively in the current directory and in the git repo directory"""
#         rootDirs.extend(scan_repos_recursively(prj_top_dir))
#         rootDirs.extend(scan_repos_recursively(git_repo_dir))
#         if confirm_dirs(rootDirs):
#             process_scanned_dirs(rootDirs)
#         else:
#             sys.exit(0)
#     else:
#         """ use the current directory and the pyLnLib directory as the root directories"""
#         rootDirs.append(pyLnLib_path)
#         rootDirs.append(prj_repo_dir)
#         if confirm_dirs(rootDirs):
#             process_this_project(rootDirs)
#         else:
#             sys.exit(0)




#     import pdb; pdb.set_trace();  # by Loreto
#     # now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
#     primary_project_description: str|None = None
#     primary_project_name: str|None = None





#     for i, gitROOT in enumerate(rootDirs, 1):
#         prj_name=Path(gitROOT).stem
#         parent=Path(gitROOT).parent

#         fCommit, fPush = gitStatus(git_dir=gitROOT)




#     for i, gitROOT in enumerate(rootDirs, 1):
#         prj_name=Path(gitROOT).stem
#         parent=Path(gitROOT).parent

#         fCommit, fPush = gitStatus(git_dir=gitROOT)

#         logger.info("")
#         logger.notify("="*50)
#         logger.notify(f"gitROOT: {parent}/{C.yellow}{prj_name}")

#         if not args.scan:
#             if prj_name == 'pyLnLib':
#                 commit_description = f"{primary_project_name}: {primary_project_description}"

#         if fCommit:
#             if args.go:
#                 commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
#                 executeCommit(gitROOT=gitROOT, commandsList=commandsList, commit_description=commit_description, fExecute=True)

#             else:
#                 commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
#                 executeCommit(gitROOT=gitROOT, commandsList=commandsList, commit_description=commit_description, fExecute=False)
#                 choice=keyboardPrompt(text_msg="enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
#                 if choice[0] == "--go":
#                     '''devo di nuovo processare, prima di procedereffettivamente,
#                         perché alcuni file potrebbero essere stati modificati
#                         (CHANGELOG.MD o pyproject.toml, o altri)'''

#                     commandsList, commit_description = processArgs(fCommit=fCommit, fPush=fPush, gitRoot=gitROOT)
#                     executeCommit(gitROOT=gitROOT, commandsList=commandsList, commit_description=commit_description, fExecute=True)

#         else:
#             logger.notify(f"{C.yellowH}{prj_name}: {C.yellow} 🚀 nothing to do!",  color=C.green)

#         if i == 1:
#             primary_project_name = prj_name
#             primary_project_description = commit_description


if __name__ == "__main__":
    main()
