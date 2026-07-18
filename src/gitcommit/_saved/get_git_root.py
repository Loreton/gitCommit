#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.44.48
#

from operator import gt
import sys; sys.dont_write_bytecode = True


### - project modules
from pyLnLib import  lnRun
from pyLnLib import  get_logger

###################################################
#
###################################################
def getGitRoot() -> str:
    logger=get_logger()
    _rcode, stdout, _stderr = lnRun( "git rev-parse --show-toplevel", fExecute=True, stacklevel=1 )
    if _rcode != 0:
        logger.error(f"getGitRoot: failed to get git root: {_stderr}", exit=True)
    return stdout.strip()
