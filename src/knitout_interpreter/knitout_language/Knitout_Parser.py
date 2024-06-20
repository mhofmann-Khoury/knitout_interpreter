"""Parser code for accessing Parglare language support"""
import re

import importlib_resources
import parglare.exceptions
from parglare import Parser, Grammar

import knitout_interpreter
from knitout_interpreter.knitout_language.knitout_actions import action
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Parser:
    """
        Parser for reading knitout using the parglare library
    """

    def __init__(self, debug_grammar: bool = False, debug_parser: bool = False, debug_parser_layout: bool = False):
        pg_resource_stream = importlib_resources.files(knitout_interpreter.knitout_language).joinpath('knitout.pg')
        self._grammar: Grammar = Grammar.from_file(pg_resource_stream, debug=debug_grammar, ignore_case=True)
        self._set_parser(debug_parser, debug_parser_layout)

    def _set_parser(self, debug_parser: bool, debug_parser_layout: bool):
        self._parser: Parser = Parser(self._grammar, debug=debug_parser, debug_layout=debug_parser_layout, actions=action.all)
        self._parser.knitout_parser = self  # make this structure available from actions

    def parse_knitout_to_instructions(self, pattern: str, pattern_is_file: bool = False,
                                      reset_parser: bool = True,
                                      debug_parser: bool = False, debug_parser_layout: bool = False) -> list[Knitout_Line]:
        """
        :param debug_parser_layout: Prints comment debugging.
        :param debug_parser: Print grammar debugging.
        :param reset_parser: Resets parser to have no prior input.
        :param pattern: Either a file or the knitout string to be parsed.
        :param pattern_is_file: If true, assume that the pattern is parsed from a file.
        :return: List of knitout instructions created by parsing given pattern.
        """
        codes: list[Knitout_Line] = []
        if reset_parser:
            self._set_parser(debug_parser, debug_parser_layout)
        if pattern_is_file:
            with open(pattern, "r") as pattern_file:
                lines = pattern_file.readlines()
        else:
            lines = pattern.splitlines()
        for i, line in enumerate(lines):
            if not re.match(r'^\s*$', line):
                try:
                    code = self._parser.parse(line)
                except parglare.exceptions.ParseError as e:
                    print(f"Knitout Parsing Error at {i}: {line}")
                    raise e
                if code is None:
                    continue
                else:
                    assert isinstance(code, Knitout_Line), f"Expected Knitout Line but got {code}"
                    codes.append(code)
        return codes


def parse_knitout(pattern: str, pattern_is_file: bool = False, debug_parser: bool = False, debug_parser_layout: bool = False) -> list[Knitout_Line]:
    """
    Executes the parsing code for the parglare parser.
    :param debug_parser_layout: Prints comment debugging.
    :param debug_parser: Print grammar debugging.
    :param pattern: Either a file or the knitout string to be parsed.
    :param pattern_is_file: If true, assume that the pattern is parsed from a file.
    :return: Version, header, separated instructions, separated comments, total instruction set with comments
    """
    parser = Knitout_Parser(debug_parser, debug_parser_layout)
    return parser.parse_knitout_to_instructions(pattern, pattern_is_file, reset_parser=False)
