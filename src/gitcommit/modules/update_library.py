#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 09-05-2026 17.01.45
#

import sys; sys.dont_write_bytecode = True
from datetime import datetime
from pathlib import Path

import json

### - project modules
from pyLnLib import  gVars as gv, lnRun



###################################################
# ---- update library.json ----
###################################################
def update_library(version: str, fExecute: bool, gitRoot: str):
    LIBRARY_FILE = gitRoot / "library.json"

    path = Path(LIBRARY_FILE)
    if not path.exists():
        gv.logger.warning("file 'library.json' NOT found, skip.")
        return False
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    old_version = data.get("version", "N/A")

    if fExecute:
        data["version"] = version
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        gv.logger.info("file: 'library.json' aggiornato: %s → %s",  old_version, version)
    else:
        # Dry-run: preview colorata
        gv.logger.info("library.json preview (dry-run):")
        gv.logger.info("  old_version: %s", old_version)
        gv.logger.info("  new_version: %s", version)

    return True




