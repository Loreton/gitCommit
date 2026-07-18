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
from     pyLnLib            import keyboardPrompt
from     pyLnLib.files     import zipDir, get_yaml_engine
from     pyLnLib.lndict     import lnDict

C=get_colors()
pv: lnDict=get_project_vars()
logger=get_logger()

from gitcommit.core import parseInput, helpCommands
from gitcommit.modules.git_commands import get_git_root, git_status, get_last_tag
from gitcommit.files.pyproject_class import PyProjectManager
from gitcommit.files.changelog import ChangeLogManager
# from gitcommit.modules.check_args import check_version
from gitcommit.modules import check_args




def prepare_cmd_list(git_prj: lnDict) -> list:
    cmd_list: list = []

    cmd_list.append("git add .")
    cmd_list.append(f"git commit -m \"{git_prj.description}\"")

    if git_prj.push:
        cmd_list.append("git push")
    if git_prj.set_tag:
        cmd_list.append(f"git tag -a v{git_prj.new_version} -m Release {git_prj.new_version}")
        cmd_list.append("git push --tags")

    return cmd_list

#===================================================
#
#===================================================
def check_pyLnLib(project: lnDict, logger_level: str="warning") -> str:
    rcode, stdout, stderr = lnRun("git log -1 --oneline", f_execute=True, cwd=project.path, stacklevel=2 )
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

    # projectsToProcess = lnDict()
    pylnlib_commit_nr = check_pyLnLib(pv.git_project["pyLnLib"])
    ### -----------------------------
    ### - - prepara un dict per contenere i progetti da fare commit/push
    ### - - tutti i flag dello stato saranno modificati a dovere
    ### - - salva su file, per analisi, i progetti da fare commit/push
    ### - - pyLnLib comunque compare....
    ### -----------------------------
    for prj_name in projects_list[:]:
        # fExecute = False
        git_project = pv.git_project[prj_name]
        git_project["name"] = prj_name

        if args.scan:
            from datetime import datetime
            now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            git_project.description=f"update on {now}" ### force
        else:
            git_project.description=f"{args.description}"

        pyproject = PyProjectManager(git_root=git_project.path) # prepara pyProject object
        chLogManager = ChangeLogManager(git_root=git_project.path) # prepara changeLog object
        if git_project.python:
            git_project.commit, git_project.push = git_status(git_root=git_project.path)
            git_project.last_tag = get_last_tag(git_root=git_project.path)
            git_project.last_version = pyproject.get_version()
            git_project.set_tag = check_args.version(git_prj=git_project)
            if git_project.set_tag:
                # - update description
                git_project.description=f"{git_project.description} (Release {git_project.new_version}) (pylnlib_commit={pylnlib_commit_nr})"
                # - update version
                pyproject.update_version(git_project.new_version, f_execute=False)
                # - update changelog
                chLogManager.update(new_version=git_project.new_version, last_tag=git_project.last_tag, f_execute=False) # Preview (dry-run)
                logger.info(f"Riepilogo commit: {chLogManager.get_summary()}")





        print(git_project); print(); logger.info("status", color=C.magentaH, exit=False)

        cmd_list: list = prepare_cmd_list(git_prj=git_project)
        for cmd in cmd_list:
            logger.info(f"{cmd}")
        choice=keyboardPrompt(text_msg="enter [--go] [ENTER]=skip", validKeys=["--go", "ENTER"], exitKeys=["x", "q"])
        if choice[0] == "--go":
            '''devo di nuovo processare, prima di procedere,
                perché alcuni file devono essere  modificati
                (CHANGELOG.MD o pyproject.toml, o altri)'''
            chLogManager.update(new_version=git_project.new_version, last_tag=git_project.last_tag, f_execute=True) # Preview (dry-run)
            pyproject.update_version(git_project.new_version, f_execute=True)
            for cmd in cmd_list:
                lnRun(command=cmd, cwd=git_project.path, f_execute=True)




    sys.exit("processo completato!")

#################################################################
#  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -  MAIN -
#################################################################

if __name__ == "__main__":
    main()
