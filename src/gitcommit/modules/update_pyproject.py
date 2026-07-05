#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-06-2026 19.53.20
#

import sys; sys.dont_write_bytecode = True
from pathlib import Path

### - project modules
from pyLnLib import  get_logger
logger = get_logger()



###################################################
# ---- update pyproject.toml ----
###################################################
def update_pyproject(new_version: str, fExecute: bool, gitRoot: str):
    pyproject = Path(gitRoot) / "pyproject.toml"

    if pyproject.exists():
        import tomllib, tomli_w
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)

        if "project" not in data:
            data["project"] = dict()
        cur_version = data["project"].get("version", "0.0.0")
        data["project"]["version"] = new_version

        if fExecute:
            with open(pyproject, mode="wb") as fp:
                tomli_w.dump(data, fp)
        else:
            # Dry-run: preview colorata
            logger.info("pyproject.toml preview (dry-run):")
            logger.info("  cur_version: %s", cur_version)
            logger.info("  new_version: %s", new_version)

    else:
        logger.warning("file 'pyproject.toml' NOT found, skipping.")
        return False

    return True
