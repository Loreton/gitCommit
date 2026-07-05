#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.53.00
#

import sys; sys.dont_write_bytecode = True


### - project modules
from pyLnLib import lnRun


###################################################
#
###################################################
def get_last_tag(gitRoot: str):
    _rcode, stdout, _stderr = lnRun("git describe --tags --abbrev=0",
                                    fExecute=True,
                                    cwd=gitRoot,
                                    stacklevel=2
                                )

    tag = stdout.strip()

    return tag if tag else "v0.0.0"
