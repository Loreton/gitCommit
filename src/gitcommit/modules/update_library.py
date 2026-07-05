#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-06-2026 20.10.42
#

import sys; sys.dont_write_bytecode = True
# from datetime import datetime
from pathlib import Path

import json

### - project modules
from pyLnLib import  get_logger
logger=get_logger()


###################################################
# ---- update library.json ----
###################################################
def update_library(version: str, fExecute: bool, gitRoot: str):
    # LIBRARY_FILE = gitRoot / "library.json"

    library_json = Path(gitRoot) / "library.json"

    if library_json.exists():
        with open(library_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        cur_version = data.get("version", "N/A")

        if fExecute:
            data["version"] = version
            with open(library_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            logger.info("file: 'library.json' aggiornato: %s → %s",  cur_version, version)
        else:
            # Dry-run: preview colorata
            logger.info("library.json preview (dry-run):")
            logger.info("  cur_version: %s", cur_version)
            logger.info("  new_version: %s", version)

    else:
        logger.warning("file 'library.json' NOT found, skip.")
        return False
    return True
