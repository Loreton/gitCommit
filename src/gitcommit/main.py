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
from pyLnLib.context    import pVars as pv
from pyLnLib.colors    import get_colors
from pyLnLib.system    import lnRun
from pyLnLib            import keyboardPrompt
from pyLnLib.files     import zipDir
from pyLnLib.lndict     import lnDict
from pyLnLib.git.pyproject_class import PyProjectManager
from pyLnLib.git.changelog_class import ChangeLogManager


from gitcommit import helpCommands
from gitcommit import get_git_root, git_status, get_last_tag
from gitcommit import initialize_program
from gitcommit.process.check_args import check_version

logger=get_logger()
C=get_colors()



#===================================================
#
#===================================================
def prepare_cmd_list(project: lnDict) -> list:
    """preparazione della command list daseguire per aggiornare git project
    """

    now = datetime.now().strftime("%Y.%m.%d")
    default_description: str= pv.args.description  or f"update on {now}" ### force

    pylnlib_commit_nr = check_pyLnLib(pv.config.git_project["pyLnLib"])
    commit_nr =  f" (pylnlib_commit={pylnlib_commit_nr})"

    commit_descr: str= f"{default_description} - (Release {project.new_version}){commit_nr}"

    if project.name == "pyLnLib":
        commit_nr =  "" # non serve mettere il commit_nr di sestesso
        if not project.pylnlib_full_update:
            commit_descr = f"update on {now} (regarding project: {pv.args.project})"

    cmd_list: list[str] = []

    if project.commit:
        cmd_list.append("git add .")

        cmd_list.append(f"git commit -m \"{commit_descr}\"")

        # va dopo il commit altrimenti non lo vede per aggiornare il CHANGELOG.md
        # if not project.just_commit:
        #     cmd_list.append("git add CHANGELOG.md")

        if project.python and not project.just_commit:
            cmd_list.append("git add pyproject.toml")


    if project.set_tag:
        cmd_list.append(f"git tag -a v{project.new_version} -m \"Release {project.new_version}\"")
        if pv.args.push:
            cmd_list.append("git push --tags")

    if pv.args.push:
        cmd_list.append("git push")


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
def process_git_repo(project: lnDict) -> None:
    logger.info("=== %s - %s ===", project.name, project.path, color=C.whiteH)
    project.commit, project.push = git_status(git_root=project.path, force_log=True)
    if project.push:
        logger.notify("some commits are pendig to be pushed!!!")
    project.last_tag = get_last_tag(git_root=project.path)
    project.curr_version = project.last_tag.lstrip('v') # type: ignore # skip 'v'

    if not project.just_commit:
        if check_version(git_prj=project): ### if project.set_tag:
            logger.notify("=== RELEASE TAG ===")
            logger.info("last tag: %s", project.last_tag)
            logger.info("new  tag: v%s", project.new_version)

            project.chLogManager.update(new_version=project.new_version, f_execute=False) # Preview (dry-run)

            if project.python:
                project.pyproject.update_version(project.new_version, f_execute=False)

            # manager = ChangeLogManager(git_root=project.path,new_version=project.new_version,last_tag=getattr(git_prj, "last_tag", None))
            # project.chLogManager.update(new_version=project.new_version, last_tag=project.last_tag, f_execute=False) # Preview (dry-run)
            # project.chLogManager.update(new_version=project.new_version, f_execute=False) # Preview (dry-run)
            # logger.info(f"Riepilogo commit: {project.chLogManager.get_summary()}")

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
                (pyproject.toml, o altri)'''

            # if not project.just_commit:
                # project.chLogManager.update(new_version=project.new_version, last_tag=project.last_tag, f_execute=True) # Preview (dry-run)
                # project.chLogManager.update(new_version=project.new_version, f_execute=True) # Preview (dry-run)
            if project.python and not project.just_commit:
                 project.pyproject.update_version(project.new_version, f_execute=True)

            for cmd in cmd_list:
                lnRun(command=cmd, cwd=project.path, f_execute=True)
            breakpoint()
            # devo farlo qui perché deve valutare dopo aver messo il tag
            project.chLogManager.update(new_version=project.new_version, f_execute=True) # Preview (dry-run)
    else:
        logger.info("=== %s - no commands to execute ===", project.name, color=C.white)
    # print("\n\n")




#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################

def main():
    ctx = initialize_program(resolve_dict_cross_references=False)
    # os.chdir('/home/loreto/filu/lnEnv')
    # -----------------------------------------
    # - print project variables if requested
    # -----------------------------------------
    if pv.args.vars:
        print(ctx.to_dict())
        sys.exit(0)

    # -----------------------------------------
    # - list commands if requested
    # -----------------------------------------
    if pv.args.list_commands:
        commands = helpCommands()
        print(f"{C.green}{commands}{C.reset}")
        sys.exit(0)


    # -----------------------------------------
    # - get current project git_dir (risale alla root del git)
    # -----------------------------------------
    this_git_dir = Path(get_git_root(os.path.curdir))
    project_dir_name = this_git_dir.name
    if project_dir_name not in pv.config.git_project:
        logger.error(f"project {project_dir_name} not found in git_project")
        logger.notify("please configure it into configuration file.", exit=True)

    # -----------------------------------------
    # - create pyLnLib.zip if requested
    # -----------------------------------------
    if pv.args.ziplib:
        pyLnLib_path = pv.root_dirs.pyLnLib_dir /  "src/pyLnLib"
        zipDir(source_dir=pyLnLib_path, output_zip=this_git_dir / "pyLnLib.zip")
        sys.exit(0)


    ### -----------------------------
    ### - crea una list per contenere i nomi dei progetti da processare
    ### -----------------------------

    projects_name_list: list[str] = [] # lista dei nomi dei progetti da processare
    project=pv.config.git_project.get(project_dir_name)
    project.main_dir_name=project_dir_name
    if project.python:
        if project.main_dir_name == 'pyLnLib':
            projects_name_list = [project.main_dir_name]
            project.pylnlib_full_update=True
        else:
            projects_name_list = ['pyLnLib', project.main_dir_name]
    else:
        projects_name_list = [project.main_dir_name]

    ### -----------------------------
    ### - - prepara un dict per contenere i progetti da fare commit/push
    ### - - tutti i flag dello stato saranno modificati a dovere
    ### - - salva su file, per analisi, i progetti da fare commit/push
    ### - - pyLnLib comunque compare....
    ### -----------------------------
    for prj_name in projects_name_list[:]:
        # - carica progetto
        project = pv.config.git_project[prj_name]

        # ----------------------
        # - modifica il nome della directory del progetto, perché non è detto che sia uguale al nome del progetto
        # - nel caso di pyLnLib viene aggiornata anche su altri progetti ma viene fatto solo un commit con relativo push
        # ----------------------
        project.main_dir_name = project_dir_name
        if project_dir_name != project.name:
            project.just_commit=True

        # --- prepara changeLog class object
        project.chLogManager = ChangeLogManager(git_root=project.path)

        if project.python:
            # --- prepara pyProject class object per pyproject.toml
            project.pyproject = PyProjectManager(git_root=project.path)
            print("\n\n")
            process_git_repo(project)
            # process_python_git_repo(project)

        else:
            print("\n\n")
            process_git_repo(project)



    sys.exit("processo completato!")

#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################

if __name__ == "__main__":
    main()
