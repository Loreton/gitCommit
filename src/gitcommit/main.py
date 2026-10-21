#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#

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
from pyLnLib            import clean_doc, keyboardPrompt
from pyLnLib.files     import zipDir
from pyLnLib.lndict     import lnDict
from pyLnLib.git import PyProjectManager
from pyLnLib.git import ChangeLogManager


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

    # now = datetime.now().strftime("%Y.%m.%d")
    # default_description: str= pv.args.description or f"update on {now}" ### force

    if project.pylnlib_required:
        pylnlib_commit_nr = check_pyLnLib(pv.config.git_project["pylnlib"])
        commit_descr: str= f"{project.description} - (Release {project.new_version}) - [{pylnlib_commit_nr = }]"
    else:
        commit_descr: str= f"{project.description} - (Release {project.new_version})"

    # if project.name == "pyLnLib":
    #     commit_nr =  "" # non serve mettere il commit_nr di sestesso
    #     if not project.pylnlib_full_update:
    #         commit_descr = f"update on {now} (regarding project: {pv.args.project_name})"

    cmd_list: list[str] = []

    if project.commit:
        cmd_list.append("git add .")

        cmd_list.append(f"git commit -m \"{commit_descr}\"")

    if pv.args.push:
        cmd_list.append("git push")

    if project.set_tag:
        cmd_list.append(f"git tag -a v{project.new_version} -m \"Release {project.new_version}\"")
        if pv.args.push:
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
def process_git_repo(project: lnDict) -> None:
    logger.info("=== %s - %s ===", project.name, project.path, color=C.whiteH)
    project.commit, project.push = git_status(git_root=project.path, force_log=True)
    if project.push:
        logger.notify("WARNING:\nsome commits are pendig to be pushed!!!")
    if not project.commit:
        logger.notify("WARNING:\nnothing to commit!!!", exit=True)

    project.last_tag = get_last_tag(git_root=project.path)
    project.curr_version = project.last_tag.lstrip('v') # type: ignore # skip 'v'


    set_tag = check_version(git_prj=project) ### if project.set_tag:
    if set_tag:
        logger.notify(clean_doc(f"""=== RELEASE TAG ===
                                    last tag: {project.last_tag}
                                    new  tag: v{project.new_version}
                                    """)
                                )
        project.chLogManager.update(new_version=project.new_version, f_execute=False) # Preview (dry-run)

        if project.is_python:
            project.pyproject.update_version(project.new_version, f_execute=False)
    else:
        logger.info(f"no tag change, {project.curr_version = }")


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

            if project.set_tag:
                project.chLogManager.update(new_version=project.new_version, f_execute=True) # Preview (dry-run)
                if project.is_python:
                     project.pyproject.update_version(project.new_version, f_execute=True)

            for cmd in cmd_list:
                lnRun(command=cmd, cwd=project.path, f_execute=True)
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
    # - get project name
    # -----------------------------------------
    current_dir = Path(get_git_root(os.path.curdir))
    project_name = current_dir.name
    if not pv.args.project_name:
        logger.error("project_name not specified, use --project_name <name>\n", exit=True)
    elif pv.args.project_name == '.':
        pass
    else:
        project_name = pv.args.project_name


    project=pv.config.git_project.get(project_name.lower(), None)
    if not project:
        logger.error(f"project {project_name} not found in configuration file\n", exit=True)

    os.chdir(project.path)
    # -----------------------------------------
    # - create pyLnLib.zip if requested
    # -----------------------------------------
    if pv.args.ziplib:
        pyLnLib_path = pv.root_dirs.pyLnLib_dir /  "src/pyLnLib"
        zipDir(source_dir=pyLnLib_path, output_zip=current_dir / "pyLnLib.zip")
        sys.exit(0)


    ### -----------------------------
    ### - Verifica se pyLnLibè  necessario
    ### -----------------------------
    if project.get('pylnlib_required', False):
        pylnlib=pv.config.git_project["pylnlib"]
        pylnlib.commit, pylnlib.push = git_status(git_root=pylnlib.path, force_log=True)
        if pylnlib.commit or pylnlib.push:
            logger.warning("WARNING: pyLnLib is required and has pending commits or push, please update it first!\n", exit=True)


    ### -----------------------------
    ### - Processiamo il progetto
    ### -----------------------------
    # --- prepara changeLog class object
    project.chLogManager = ChangeLogManager(git_root=project.path)

    if project.is_python:
        # --- prepara pyProject class object per pyproject.toml
        project.pyproject = PyProjectManager(git_root=project.path)

    project.description= pv.args.description or f"update on {datetime.now().strftime('%Y.%m.%d %H:%M:%S')}" ### force
    print("\n\n")
    process_git_repo(project)

    sys.exit("processo completato!")

#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################

if __name__ == "__main__":
    main()
