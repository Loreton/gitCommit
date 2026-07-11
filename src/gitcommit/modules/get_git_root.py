#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.44.48
#

import sys; sys.dont_write_bytecode = True


### - project modules
from pyLnLib import  lnRun


###################################################
#
###################################################
def getGitRoot():
    _rcode, stdout, _stderr = lnRun( "git rev-parse --show-toplevel", fExecute=True, stacklevel=1 )
    return stdout.strip()
