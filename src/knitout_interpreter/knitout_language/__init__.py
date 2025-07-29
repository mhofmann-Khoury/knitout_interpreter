"""
knitout_language: Parsing and grammar support for knitout files.

This module provides the parsing infrastructure for knitout files, including grammar definitions, parser actions, and execution context management.
It handles the conversion from raw knitout text files into structured Python objects thatcan be executed on virtual knitting machines.

Key Components:
    - Knitout_Parser: Main parser class using Parglare for grammar-based parsing
    - parse_knitout: Convenience function for parsing knitout files or strings
    - Knitout_Context: Manages the state and context during knitout execution
    - knitout_actions: Parser action functions that convert grammar matches to objects
    - Grammar files: <knitout.pg> and <knitout.pgt> contain the formal grammar definition

Parsing Process:
    1. Raw knitout text is tokenized according to the grammar.
    2. Parser actions convert tokens into instruction objects.
    3. Context manager organizes instructions into executable sequences.
    4. Instructions can be executed on virtual knitting machines.

Example:
    Parse a knitout file:

    >>> from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
    >>> instructions = parse_knitout("pattern.k", pattern_is_file=True)
    >>> print(f"Parsed {len(instructions)} instructions")

    Use the parser directly for more control:

    >>> from knitout_interpreter.knitout_language.Knitout_Parser import Knitout_Parser
    >>> parser = Knitout_Parser(debug_parser=True)
    >>> instructions = parser.parse_knitout_to_instructions("knit + f1 1")

    Manage execution context:

    >>> from knitout_interpreter.knitout_language.Knitout_Context import Knitout_Context
    >>> context = Knitout_Context()
    >>> instructions, machine, graph = context.process_knitout_file("pattern.k")

Grammar Support:
    The parsing is based on a formal grammar definition that supports:
    - All knitout v2 specification instructions
    - Header declarations (machine, gauge, yarn, carriers, position)
    - Comments and version specifications
    - Proper error handling and reporting
"""

# Import the main parsing functionality
from .Knitout_Parser import parse_knitout, Knitout_Parser
from .Knitout_Context import Knitout_Context

# Import parser actions (advanced users might need these)
from .knitout_actions import action

# Define what gets imported with "from knitout_language import *"
__all__ = [
    # Main parsing functions - most commonly used
    "parse_knitout",  # Convenience function for quick parsing
    "Knitout_Parser",  # Full parser class for advanced control

    # Context management
    "Knitout_Context",  # Execution context and state management
]

# Module constants
GRAMMAR_FILE = "knitout.pg"
SUPPORTED_KNITOUT_VERSIONS = [2]


def get_supported_versions() -> list[int]:
    """Get list of supported knitout specification versions.

    Returns:
        List of integer version numbers that this parser supports.
    """
    return SUPPORTED_KNITOUT_VERSIONS.copy()


# Add utility functions to __all__
__all__.extend([
    "get_supported_versions",
    "SUPPORTED_KNITOUT_VERSIONS"
])

# Documentation for submodule organization
__doc__ += """

Submodule Organization:
    Knitout_Parser.py: Main parser implementation using Parglare
    Knitout_Context.py: Execution context and state management
    knitout_actions.py: Parser action functions for grammar reduction
    knitout.pg: Grammar file defining knitout language syntax
    knitout.pgt: Compiled grammar table (generated automatically)

Usage Patterns:
    Simple parsing (most common):
        from knitout_interpreter.knitout_language import parse_knitout

    Advanced parsing control:
        from knitout_interpreter.knitout_language import Knitout_Parser

    Execution context management:
        from knitout_interpreter.knitout_language import Knitout_Context
"""
