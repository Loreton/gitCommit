#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 09-05-2026 17.01.02
#

import sys; sys.dont_write_bytecode = True


### - project modules
from pyLnLib import  gVars as gv, lnRun

###################################################
#
###################################################
def getGitRoot():
    rcode, stdout, stderr = lnRun(
        "git rev-parse --show-toplevel",
        fExecute=True,
        toLogger=gv.logger,
        stacklevel=1
    )
    return stdout.strip()

