"""
knitout_interpreter: A comprehensive library for interpreting knitout files.

This package provides tools for parsing, validating, and executing knitout files
used to control automatic V-Bed knitting machines. It includes support for the
complete Knitout specification v2 created by McCann et al.

The library bridges the gap between high-level knitting pattern descriptions and
machine-level execution, providing comprehensive analysis and simulation capabilities.

Core Functionality:
    - run_knitout(): Simple function to parse and execute knitout files
    - Knitout_Executer: Advanced class for detailed analysis and execution control

For specialized functionality, import from submodules:
    - knitout_interpreter.knitout_operations: Individual instruction types
    - knitout_interpreter.knitout_language: Parsing and grammar support
    - knitout_interpreter.knitout_execution_structures: Execution data structures

Example:
    Basic usage - execute a knitout file:

    >>> from knitout_interpreter.run_knitout import run_knitout
    >>> instructions, machine, graph = run_knitout("pattern.k")
    >>> print(f"Executed {len(instructions)} instructions")

    Advanced analysis with detailed control:

    >>> from knitout_interpreter import Knitout_Executer
    >>> from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
    >>> from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    >>>
    >>> instructions = parse_knitout("pattern.k", pattern_is_file=True)
    >>> executer = Knitout_Executer(instructions, Knitting_Machine())
    >>> print(f"Execution time: {executer.execution_time} carriage passes")
    >>> print(f"Width required: {executer.left_most_position} to {executer.right_most_position}")
"""

# Import version information (single source of truth)
from ._version import __version__

# Core functionality - the main public API
from .run_knitout import run_knitout
from .knitout_execution import Knitout_Executer

# Define the minimal public API - only core functions
__all__ = [
    "__version__",
    "run_knitout",  # Simple execution function for most users
    "Knitout_Executer",  # Advanced analysis class
]

# Package metadata
__author__ = "Megan Hofmann"
__email__ = "m.hofmann@northeastern.edu"
__license__ = "MIT"
__description__ = "Support for interpreting knitout files used for controlling automatic V-Bed Knitting machines."

# Package constants (not in __all__ - available but not imported by star import)
DEFAULT_KNITOUT_VERSION = 2
SUPPORTED_MACHINE_TYPES = [
    "SWG091N2",  # Shima Seiki machines
]


# Utility functions (not in __all__ - available but not imported by star import)
def get_version() -> str:
    """Get the current version of knitout_interpreter.

    Returns:
        The version string from the package metadata.
    """
    return __version__


# Additional metadata for programmatic access
def get_package_info() -> dict[str, str]:
    """Get comprehensive package information.

    Returns:
        Dictionary containing package metadata including information
        from both the package and pyproject.toml.
    """
    return {
        "name": "knitout-interpreter",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "homepage": "https://github.com/mhofmann-Khoury/knitout_interpreter",
        "repository": "https://github.com/mhofmann-Khoury/knitout_interpreter",
        "documentation": "https://github.com/mhofmann-Khoury/knitout_interpreter#readme",
        "bug_tracker": "https://github.com/mhofmann-Khoury/knitout_interpreter/issues",
        "pypi": "https://pypi.org/project/knitout-interpreter/",
    }


def get_supported_machines() -> list[str]:
    """Get list of supported machine types.

    Returns:
        List of machine type strings that are supported by this library.
    """
    return SUPPORTED_MACHINE_TYPES.copy()
