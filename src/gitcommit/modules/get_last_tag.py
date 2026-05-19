#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 09-05-2026 17.01.13
#

import sys; sys.dont_write_bytecode = True


### - project modules
from pyLnLib import  gVars as gv, lnRun


###################################################
#
###################################################
def get_last_tag(gitRoot: str):
    rcode, stdout, stderr = lnRun("git describe --tags --abbrev=0",
                                    fExecute=True,
                                    cwd=gitRoot,
                                    toLogger=gv.logger,
                                    stacklevel=2
                                )

    tag = stdout.strip()

    return tag if tag else "v0.0.0"


