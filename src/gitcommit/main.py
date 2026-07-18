#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2026 19.53.19
#

# from inspect import stack
import sys

# sys.dont_write_bytecode = True
import os
from pathlib import Path

     ### - project modules
# from gitcommit.files.changelog import generate_changelog
from     pyLnLib.context   import ctx, get_project_vars
from     pyLnLib.colors    import get_colors
from     pyLnLib.logger    import get_logger, init_logger
from     pyLnLib.system    import lnRun
# from     pyLnLib            import keyboardPrompt
from     pyLnLib.files     import zipDir, get_yaml_engine
from     pyLnLib.lndict     import lnDict

C=get_colors()
pv: lnDict=get_project_vars()
logger=get_logger()

from gitcommit.core import parseInput, helpCommands
from gitcommit.modules.git_commands import get_git_root, git_status, get_last_tag
from gitcommit.files.pyproject_class import PyProjectManager
from gitcommit.files.changelog import ChangeLogManager
from gitcommit.modules.check_args import check_version



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
    if 'debugpy' in sys.modules:
        print(os.environ.get("ZED_APP_PATH"))
        print(os.environ.get("ZED_ENVIRONMENT"))
        print(os.environ.get("ZED_TERM"))
        print(os.environ.get("TERM_PROGRAM"))

    ctx.set_project_name("gitCommit")

    #### 1. logger initializzation
    logger=init_logger(logger_name="gitCommit", test=False)

    #### 2. read static project_list file
    yaml_engine=get_yaml_engine(search_paths=[ctx.get_conf_dir()], recursive=True)
    config_file = ctx.get_conf_dir() / "projects_list.yaml"
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))

    #### 3. initialize project variables (pv)
    pv.update(config_data)

    #### 4. processo input arguments....
    args = parseInput()
    pv["input_args"]=vars(args) # include args in project_vars
    pv.save_yaml(filepath=ctx.get_log_dir() / "project_vars.yaml", title="project_vars", indent=4)

    # -----------------------------------------
    # - update logger as requested by input arguments
    # -----------------------------------------
    logger.setShowCaller(show_caller=args.log_show_caller)

    # -----------------------------------------
    # - print project variables if requested
    # -----------------------------------------
    if args.vars:
        print(pv)
        sys.exit(0)

    # -----------------------------------------
    # - list commands if requested
    # -----------------------------------------
    if args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)


    # -----------------------------------------
    # - get current project git_dir
    # -----------------------------------------
    this_git_dir = Path(get_git_root(os.path.curdir))

    # -----------------------------------------
    # - create pyLnLib.zip if requested
    # -----------------------------------------
    if args.ziplib:
        pyLnLib_path = pv.root_dirs.pyLnLib_dir /  "src/pyLnLib"
        zipDir(source_dir=pyLnLib_path, output_zip=this_git_dir / "pyLnLib.zip")
        sys.exit(0)




    ### -----------------------------
    ### - crea una list per contenere i nomi dei progetti da processare
    ### -----------------------------
    projects_list: list[str] = [] # lista dei nomi dei progetti da processare
    if args.scan:
        projects_list = pv.git_project.keys() # leggili dalla configurazione
    else:
        projects_list = [this_git_dir.name]
        # git_prj=pv.git_project[prj_git_dir.name]

    projectsToProcess = lnDict()
    pylnlib_commit_nr = check_pyLnLib(pv.git_project["pyLnLib"])
    ### -----------------------------
    ### - - prepara un dict per contenere i progetti da fare commit/push
    ### - - tutti i flag dello stato saranno modificati a dovere
    ### - - salva su file, per analisi, i progetti da fare commit/push
    ### - - pyLnLib comunque compare....
    ### -----------------------------
    for prj_name in projects_list[:]:
        git_project = pv.git_project[prj_name]
        git_project["name"] = prj_name

        if git_project.python:
            git_project.commit, git_project.push = git_status(git_root=git_project.path)
            git_project.last_tag = get_last_tag(git_root=git_project.path)
            pyproject = PyProjectManager(git_root=git_project.path) # prepara pyProject objec
            git_project.last_version = pyproject.get_version()
            check_version(git_prj=git_project)
            if args.changelog:
                manager = ChangeLogManager(git_root=git_project.path, new_version=git_project.new_version, last_tag=git_project.last_tag)
                # Preview (dry-run)
                manager.update(f_execute=args.go)
                # Stampa riepilogo
                summary = manager.get_summary()
                logger.info(f"Riepilogo commit: {summary}")
                print(git_project); print(); logger.info("uscita temporanea", color=C.magentaH, exit=True)



            if args.scan:
                from datetime import datetime
                now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
                commit_description =f"update on {now}" ### force
            else:
                commit_description=f"{args.description} (Release {git_project.new_version})"



            # cmd_list, commit_description = check_args(git_prj=git_project)
            # git_project["cmd_list"] = cmd_list
            git_project["commit_description"] = commit_description
            git_project["flags.pylnlib_commit_nr"] = pylnlib_commit_nr
        # if process_project(project=git_project):
            # projectsToProcess[prj_name] = git_project

    projectsToProcess.save_yaml(filepath=ctx.get_log_dir() / "project_vars_final.yaml", title="projects_to_be_committed", indent=4)

    for prj_name in projectsToProcess.keys():
        git_project = projectsToProcess[prj_name]
        if git_project.cmd_list:
            ...
            # commit_project(project=git_project)
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
#     pv.update(loadJsonVarsStruct())

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
