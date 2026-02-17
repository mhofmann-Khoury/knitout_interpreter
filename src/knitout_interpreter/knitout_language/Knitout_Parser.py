"""Parser code for accessing Parglare language support"""

from __future__ import annotations

import re

import parglare.exceptions
from importlib_resources import files
from parglare import Grammar, Parser

import knitout_interpreter
from knitout_interpreter.knitout_errors.Knitout_Error import Incomplete_Knitout_Line_Error, Knitout_ParseError
from knitout_interpreter.knitout_execution_structures.knitout_program import Knitout_Program
from knitout_interpreter.knitout_language.knitout_actions import action
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Parser:
    """Parser for reading knitout using the parglare library."""

    _KNITOUT_GRAMMAR_FILENAME: str = "knitout.pg"  # The name of the knitout grammar file

    def __init__(self, debug_grammar: bool = False, debug_parser: bool = False, debug_parser_layout: bool = False) -> None:
        """Initialize the Knitout parser with optional debugging features.

        Args:
            debug_grammar (bool, optional): Enable grammar debugging. Defaults to False.
            debug_parser (bool, optional): Enable parser debugging. Defaults to False.
            debug_parser_layout (bool, optional): Enable parser layout debugging. Defaults to False.

        Raises:
            FileNotFoundError: If the <knitout.pg> grammar file cannot be located in the package.
        """
        try:
            grammar_file = files(knitout_interpreter.knitout_language).joinpath(self._KNITOUT_GRAMMAR_FILENAME)
            self._grammar: Grammar = Grammar.from_file(grammar_file, debug=debug_grammar, ignore_case=True)
        except (FileNotFoundError, AttributeError) as e:
            e.add_note(f"Could not locate {self._KNITOUT_GRAMMAR_FILENAME} in package {knitout_interpreter.knitout_language}. ")
            raise e from None
        self._grammar: Grammar = Grammar.from_file(grammar_file, debug=debug_grammar, ignore_case=True)
        self._parser: Parser = Parser(self._grammar, debug=debug_parser, debug_layout=debug_parser_layout, actions=action.all)

    def parse_knitout_to_instructions(self, pattern: str, pattern_is_file: bool = False) -> Knitout_Program:
        """Parse knitout pattern into a knitout program.

        Args:
            pattern (str): Either a file path or the knitout string to be parsed.
            pattern_is_file (bool, optional) : If True, treat pattern as a file path. Defaults to True.

        Returns:
            Knitout_Line: The program ordered by the parsed lines of knitout code.

        Raises:
            Knitout_ParseError: If there's an error parsing the knitout code.
            Incomplete_Knitout_Line_Error: If a knitout line processes into an incomplete code.
        """
        codes: list[Knitout_Line] = []
        if pattern_is_file:
            with open(pattern) as pattern_file:
                lines = pattern_file.readlines()
        else:
            lines = pattern.splitlines()
        for i, line in enumerate(lines):
            if not re.match(r"^\s*$", line):
                try:
                    code = self._parser.parse(line, extra=i)
                except parglare.exceptions.SyntaxError as e:
                    raise Knitout_ParseError(i, line, e) from None
                if code is None:
                    continue
                elif not isinstance(code, Knitout_Line):
                    raise Incomplete_Knitout_Line_Error(i, line) from None
                else:
                    codes.append(code)
        return Knitout_Program(codes)


def parse_knitout(pattern: str, pattern_is_file: bool = False) -> Knitout_Program:
    """Execute the parsing code for the parglare parser.

    This is a convenience function that creates a Knitout_Parser instance and parses the given pattern.

    Args:
        pattern (str): Either a file path or the knitout string to be parsed.
        pattern_is_file (bool, optional) : If True, treat pattern as a file path. Defaults to True.

    Returns:
        list[Knitout_Line]: List of knitout lines created by parsing the given pattern.
    """
    parser = Knitout_Parser()
    return parser.parse_knitout_to_instructions(pattern, pattern_is_file)
