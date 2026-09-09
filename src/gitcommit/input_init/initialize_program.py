# /home/loreto/filu/Programming/gitREPO/lnSync/src/lnsync/core/initialize_project.py
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)

from pathlib import Path



# --- pyLnLib modules
from pyLnLib.git        import PyProjectManager
from pyLnLib.context   import ctx, lnContext, pVars as pv
from pyLnLib.files     import get_yaml_engine
from pyLnLib.lndict    import lnDict
from pyLnLib.logger    import get_logger
from pyLnLib.colors    import get_colors
from pyLnLib.system import start_signal_handler



# --- project modules
from .parse_input import parseInput


logger=get_logger()
C=get_colors()



#==================================
def _read_pyproject() -> str:
    """
         read pyproject.toml filr to extract program version

         Args:
             None

         return:
             application version (str)
    """
    pyproject = PyProjectManager(Path.cwd())
    return pyproject.get_version()


#==================================
def _read_configuration(project_name: str, resolve_dict: bool=False) -> lnDict:
    """
         read application configuration file

         Args:
             None

         return:
             configuration (lnDict)
    """

    config_file = pv.config_dir / f"{project_name}_config.yaml"
    yaml_engine=get_yaml_engine(search_paths=[pv.config_dir], recursive=True)
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))
    config_data.save_yaml(title="processed_config", filepath=pv.log_dir / f"{project_name}_config.yaml")

    if resolve_dict:
        config_data.resolve_cross_references()
        config_data.save_yaml(title="resolved_config", filepath=pv.log_dir / f"{project_name}_config_after_resolve.yaml")

    return config_data






#=================================================
# setup principali funzioni per il programma
#   crx.project_name        project name
#   crx.project_temp_dir    project temp dir
#   crx.project_config_dir  project config dir
#   crx.config_data         project configuration data
#   crx.args                input arguments
#   logger                  initialize logger
#=================================================
def initialize_program(resolve_dict_cross_references=False) -> lnContext:
    project_name: str = "gitCommit"

    start_signal_handler(True)

    #read=============================================
    # 1. initialize context
    #================================================
    appl_version = _read_pyproject()
    ctx.initialize(project_name=project_name, project_temp_dir=f"/tmp/{project_name}-{appl_version}", version=appl_version)


    #### 2. logger initializzation
    default_console_logger_level="info"
    logger.initialize(name=project_name, logging_dir=pv.log_dir, console_logger_level=default_console_logger_level)
    pv.logger = logger # potrebbe tornare utile

    #================================================
    # 3.  read  project configuration file
    # 3a. insert configuration data into context
    #================================================
    config_data=_read_configuration(project_name=project_name, resolve_dict=resolve_dict_cross_references)
    pv.config.update(config_data)


    #================================================
    # 2. read inout args
    #================================================
    args = parseInput()
    pv.args.update(vars(args)) # trasformiamolo in lnDict()
    if args.console_log_level != default_console_logger_level:
        logger.setConsoleLoggerLevel(args.console_log_level)


    return ctx
