#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2026 19.53.19
#

# from inspect import stack
from fcntl import F_ADD_SEALS
import sys
# from webbrowser import get; sys.dont_write_bytecode = True
import os
from pathlib import Path
from datetime import datetime
# from timeit import default_timer

     ### - project modules
# from gitcommit.files.changelog import generate_changelog
from     pyLnLib.context   import ctx, get_project_vars
from     pyLnLib.colors    import get_colors
from     pyLnLib.logger    import get_logger, init_logger
from     pyLnLib.system    import lnRun
from     pyLnLib            import keyboardPrompt
from     pyLnLib.files     import zipDir, get_yaml_engine
from     pyLnLib.lndict     import lnDict
from pyLnLib.git.pyproject_class import PyProjectManager
from pyLnLib.git.changelog_class import ChangeLogManager

C=get_colors()
pv: lnDict=get_project_vars()
logger=get_logger()

from gitcommit.core import parseInput, helpCommands
from gitcommit.modules.git_commands import get_git_root, git_status, get_last_tag
from gitcommit.modules import check_args




#===================================================
#
#===================================================
def prepare_cmd_list(project: lnDict, n_prj: int) -> list:
    args=get_project_vars("input_args")

    now = datetime.now().strftime("%Y.%m.%d")
    default_description: str=f"update on {now}" ### force
    pylnlib_commit_nr = check_pyLnLib(pv.git_project["pyLnLib"])

    minimal = False
    if n_prj==1: # solo pyLnLib
        commit_nr =  ""
        minimal = False

    elif n_prj==2 and project.name == "pyLnLib":
        commit_nr =  ""
        minimal = True

    elif n_prj==2:
        commit_nr =  f" (pylnlib_commit={pylnlib_commit_nr})"
        minimal = False

    else:
        commit_nr =  f" (pylnlib_commit={pylnlib_commit_nr})"
        minimal = True


    commit_descr: str= f"{default_description} - (Release {project.new_version}){commit_nr}"
    cmd_list: list[str] = []


    if project.commit:
        cmd_list.append("git add .")

        if project.update_changelog:
            cmd_list.append("git add CHANGELOG.md")

        if project.update_pyproject:
            cmd_list.append("git add pyproject.toml")

        cmd_list.append(f"git commit -m \"{commit_descr}\"")


    if project.push or (args.push and project.commit):
        cmd_list.append("git push")

    if project.set_tag and not minimal:
        cmd_list.append(f"git tag -a v{project.new_version} -m \"Release {project.new_version}\"")
        if project.push:
            cmd_list.append("git push --tags")

    return cmd_list

#===================================================
#
#===================================================
def check_pyLnLib(project: lnDict, logger_level: str="warning") -> str:
    rcode, stdout, stderr = lnRun("git log -1 --oneline", f_execute=True, cwd=project.path, stacklevel=0 )
    if rcode != 0:
        logger.error(f"getGitRoot: failed to get git root: {stderr}", exit=True)
    return  stdout.split()[0]


#===================================================
#
#===================================================
def process_python_git_repo(project: lnDict, n_prj: int) -> None:
    logger.info("=== %s - %s ===", project.name, project.path, color=C.whiteH)
    project.commit, project.push = git_status(git_root=project.path, logger_level="info")
    project.last_tag = get_last_tag(git_root=project.path)
    project.curr_version = project.pyproject.get_version()
    if project.update_tag:
        project.set_tag = check_args.version(git_prj=project)
    else:
        project.set_tag = False
        project.new_version = project.curr_version

    if project.set_tag:
        if project.update_pyproject:
            project.pyproject.update_version(project.new_version, f_execute=False)
        if project.update_changelog:
            project.chLogManager.update(new_version=project.new_version, last_tag=project.last_tag, f_execute=False) # Preview (dry-run)
        logger.info(f"Riepilogo commit: {project.chLogManager.get_summary()}")

    logger.debug(f"{C.white}{project.name}:{C.info} {str(project)}")

    cmd_list: list = prepare_cmd_list(project=project, n_prj=n_prj)
    if cmd_list:
        for cmd in cmd_list:
            logger.info(f"{cmd}")
        choice=keyboardPrompt(text_msg=f"{C.white}[{project.name}] {C.yellow}enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
        if choice[0] == "--go":
            '''devo di nuovo processare, prima di procedere,
                perché alcuni file devono essere  modificati
                (CHANGELOG.MD o pyproject.toml, o altri)'''
            if project.update_changelog:
                project.chLogManager.update(new_version=project.new_version, last_tag=project.last_tag, f_execute=True) # Preview (dry-run)
                # cmd_list.insert(1, "git add CHANGELOG.md")
            if project.update_pyproject:
                project.pyproject.update_version(project.new_version, f_execute=True)
                # cmd_list.insert(1, "git add pyproject.toml")
            for cmd in cmd_list:
                lnRun(command=cmd, cwd=project.path, f_execute=True)
    else:
        logger.info("=== %s - no commands to execute ===", project.name, color=C.white)
    # print("\n\n")




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
    config_file = ctx.get_conf_dir() / "projects_name_list.yaml"
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
    projects_name_list: list[str] = [] # lista dei nomi dei progetti da processare
    # is_just_pyLnLib: bool= False

    # now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    # now = datetime.now().strftime("%Y.%m.%d")
    # default_description=f"update on {now}" ### force





    if args.all:
        projects_name_list = list(pv.git_project.keys()) # leggili dalla configurazione
        projects_name_list.remove("pyLnLib") # rimuovi temporaneamente pyLnLib
        projects_name_list.insert(0, 'pyLnLib') # inseriscila per prima in modo da poter catturare il commit_nr

    elif this_git_dir.name == 'pyLnLib':
        projects_name_list = ['pyLnLib']

    else:
        projects_name_list = ['pyLnLib', this_git_dir.name]

        # project.pyproject.update_version(project.new_version, f_execute=False)
        # project.chLogManager.update(new_version=project.new_version, last_tag=project.last_tag, f_execute=False) # Preview (dry-run)
        # logger.info(f"Riepilogo commit: {project.chLogManager.get_summary()}")


    ### -----------------------------
    ### - - prepara un dict per contenere i progetti da fare commit/push
    ### - - tutti i flag dello stato saranno modificati a dovere
    ### - - salva su file, per analisi, i progetti da fare commit/push
    ### - - pyLnLib comunque compare....
    ### -----------------------------
    n_prj: int= len(projects_name_list)
        # n_prj = len(projects_name_list)
    for prj_name in projects_name_list[:]:
        if prj_name not in pv.git_project:
            logger.error(f"project {prj_name} not found in git_project")
            logger.notify("please configure it into configuration file.", exit=True)

        git_project = pv.git_project[prj_name]

        # solo pyLnLib
        if n_prj==1:
            git_project.update_changelog=True
            git_project.update_pyproject=True
            git_project.update_tag=True

        # solo current directory
        elif n_prj==2 and git_project.name != "pyLnLib":
            git_project.update_changelog=True
            git_project.update_pyproject=True
            git_project.update_tag=True


        git_project.chLogManager = ChangeLogManager(git_root=git_project.path) # prepara changeLog object
        if git_project.python:
            git_project.pyproject = PyProjectManager(git_root=git_project.path) # prepara pyProject object
            print("\n\n")
            process_python_git_repo(git_project, n_prj=n_prj)




    sys.exit("processo completato!")

#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################

if __name__ == "__main__":
    main()
