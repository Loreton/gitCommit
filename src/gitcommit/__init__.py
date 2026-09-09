# updated by ...: Loreto Notarantonio
# ruff: noqa I001 - Import block is un-sorted or un-formatted help: Organize imports (Ruff I001)
#
__version__ = "0.1.0"

# src/gitcommit/__init__.py
# from .main import main
# from .modules.process_args import processArgs
# from .modules.parse_input import parseInput
# from .modules.git_status import gitStatus
# from .modules.get_git_root import getGitRoot
from .process.check_args import version
from .input_init import parseInput, helpCommands
from .input_init import initialize_program

from .process.git_commands import ( get_git_root,
                                    get_last_tag,
                                    git_status,
                                    is_git_repo,
                                    )


__all__ = [
    'helpCommands',
    'parseInput',
    'git_status',
    'get_git_root',
    'get_last_tag',
    'is_git_repo',
    'version',
    'initialize_program',
]
