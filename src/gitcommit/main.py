#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#

from logging import getLevelName
import sys
import os
from pathlib import Path
from datetime import datetime

     ### - project modules
# from gitcommit.files.changelog import generate_changelog
from pyLnLib.logger    import get_logger
from pyLnLib.context   import ctx, lnContext
from pyLnLib.colors    import get_colors
from pyLnLib.system    import lnRun
from pyLnLib            import keyboardPrompt
from pyLnLib.files     import zipDir, get_yaml_engine
from pyLnLib.lndict     import lnDict
from pyLnLib.git.pyproject_class import PyProjectManager
from pyLnLib.git.changelog_class import ChangeLogManager


from gitcommit.core import parseInput, helpCommands
from gitcommit.modules.git_commands import get_git_root, git_status, get_last_tag
from gitcommit.modules import check_args

logger=get_logger()
C=get_colors()



#===================================================
#
#===================================================
def prepare_cmd_list(project: lnDict) -> list:
    args=ctx.input_args
    pv=ctx.config

    now = datetime.now().strftime("%Y.%m.%d")
    default_description: str= args.description  or f"update on {now}" ### force


    pylnlib_commit_nr = check_pyLnLib(pv.git_project["pyLnLib"])
    commit_nr =  f" (pylnlib_commit={pylnlib_commit_nr})"
    # if project.update_complete:

    commit_descr: str= f"{default_description} - (Release {project.new_version}){commit_nr}"

    if project.name == "pyLnLib":
        commit_nr =  "" # non serve mettere il commit_nr di sestesso
        if not project.lnlib_complete:
            commit_descr = f"update on {now} (regarding project: {args.project})"

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

    if project.set_tag and project.update_complete:
        cmd_list.append(f"git tag -a v{project.new_version} -m \"Release {project.new_version}\"")
        if project.push or (args.push and project.commit):
            cmd_list.append("git push --tags")

    return cmd_list

#===================================================
# get last commit
#===================================================
def check_pyLnLib(project: lnDict, logger_level: str="warning") -> str:
    rcode, stdout, stderr = lnRun("git log -1 --oneline", f_execute=True, cwd=project.path, stacklevel=0)
    if rcode != 0:
        logger.error(f"getGitRoot: failed to get git root: {stderr}", exit=True)
    return  stdout.split()[0]


#===================================================
#
#===================================================
def process_python_git_repo(project: lnDict) -> None:
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

    cmd_list: list = prepare_cmd_list(project=project)
    if cmd_list:
        logger.notify(f"=== Command list for {project.name} ===")
        for cmd in cmd_list:
            logger.info(f"{cmd}")
        choice=keyboardPrompt(text_msg=f"{C.white}[{project.name}] {C.yellow}enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
        if choice[0] == "--go":
            '''devo di nuovo processare, prima di procedere,
                perché alcuni file devono essere  modificati
                (CHANGELOG.MD o pyproject.toml, o altri)'''
            if project.update_changelog:
                project.chLogManager.update(new_version=project.new_version, last_tag=project.last_tag, f_execute=True) # Preview (dry-run)

            if project.update_pyproject:
                project.pyproject.update_version(project.new_version, f_execute=True)

            for cmd in cmd_list:
                lnRun(command=cmd, cwd=project.path, f_execute=True)
    else:
        logger.info("=== %s - no commands to execute ===", project.name, color=C.white)
    # print("\n\n")



def initialize_program() -> lnContext:
    # 1. initialize context
    pyproject = PyProjectManager(Path.cwd())
    appl_version = pyproject.get_version()
    ctx.initialize(project_name="eBooks", project_temp_dir=f"/tmp/ebooks-{appl_version}", version=appl_version)


    #### 3. read  project configuration file
    config_file = ctx.project_config_dir / "projects_name_list.yaml"
    yaml_engine=get_yaml_engine(search_paths=[ctx.project_config_dir], recursive=True)
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))
    config_data.save_yaml(title="processed_config", filepath=ctx.project_log_dir / "ebooks_config.yaml")
    #### 4. insert configuration data into context
    ctx.config.update(config_data)
    return ctx

#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################

def main():
    initialize_program()
    args=parseInput()
    # - update logger as requested by input arguments
    ctx.input_args.update(vars(args)) # include args in project_vars

    #### 2. logger initializzation
    logger.initialize(name=f"gitCommit-{ctx.version}", logging_dir=ctx.project_log_dir, console_logger_level=args.console_log_level)


    # -----------------------------------------
    # -----------------------------------------
    lnDict(ctx.to_dict()).save_yaml(filepath=ctx.project_log_dir / "project_vars.yaml", title="project_vars", indent=4)


    # -----------------------------------------
    # - print project variables if requested
    # -----------------------------------------
    if args.vars:
        print(ctx.to_dict())
        sys.exit(0)

    # -----------------------------------------
    # - list commands if requested
    # -----------------------------------------
    if args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)


    # -----------------------------------------
    # - get current project git_dir (risale alla root del git)
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

    git_project_name=args.project


    if args.project == 'all':
        args.all = True
        projects_name_list = list(ctx.config.git_project.keys()) # leggili dalla configurazione
        projects_name_list.remove("pyLnLib") # rimuovi temporaneamente pyLnLib
        projects_name_list.insert(0, 'pyLnLib') # inseriscila per prima in modo da poter catturare il commit_nr
        lnlib_full_update =False
        project_full_update=False

    elif args.project == 'pyLnLib':
        projects_name_list = ['pyLnLib']
        lnlib_full_update=True
        project_full_update=True # deve includere tags, CHANGELOG.md, pyproject.toml

    else:
        projects_name_list = ['pyLnLib', this_git_dir.name]
        lnlib_full_update =False
        project_full_update=True




    ### -----------------------------
    ### - - prepara un dict per contenere i progetti da fare commit/push
    ### - - tutti i flag dello stato saranno modificati a dovere
    ### - - salva su file, per analisi, i progetti da fare commit/push
    ### - - pyLnLib comunque compare....
    ### -----------------------------
    for prj_name in projects_name_list[:]:
        if prj_name not in ctx.config.git_project:
            logger.error(f"project {prj_name} not found in git_project")
            logger.notify("please configure it into configuration file.", exit=True)

        project = ctx.config.git_project[prj_name]

        if project.name == "pyLnLib":
            project.lnlib_complete = lnlib_full_update
            project.update_changelog = lnlib_full_update
            project.update_pyproject = lnlib_full_update
            project.update_tag = lnlib_full_update
            project.update_complete = lnlib_full_update
        else:
            project.lnlib_complete = lnlib_full_update
            project.update_changelog = project_full_update
            project.update_pyproject = project_full_update
            project.update_tag = project_full_update
            project.update_complete = project_full_update


        project.chLogManager = ChangeLogManager(git_root=project.path) # prepara changeLog object
        if project.python:
            project.pyproject = PyProjectManager(git_root=project.path) # prepara pyProject object
            print("\n\n")
            process_python_git_repo(project)




    sys.exit("processo completato!")

#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################

if __name__ == "__main__":
    main()
