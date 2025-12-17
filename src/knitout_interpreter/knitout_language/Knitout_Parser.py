"""Parser code for accessing Parglare language support"""

import re

import parglare.exceptions
from importlib_resources import files
from parglare import Grammar, Parser

import knitout_interpreter
from knitout_interpreter.knitout_errors.Knitout_Error import Incomplete_Knitout_Line_Error, Knitout_ParseError
from knitout_interpreter.knitout_language.knitout_actions import action
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_BreakPoint, Knitout_Comment_Line, Knitout_Line, Knitout_No_Op


class Knitout_Parser:
    """Parser for reading knitout using the parglare library."""

    def __init__(self, debug_grammar: bool = False, debug_parser: bool = False, debug_parser_layout: bool = False) -> None:
        """Initialize the Knitout parser with optional debugging features.

        Args:
            debug_grammar: Enable grammar debugging. Defaults to False.
            debug_parser: Enable parser debugging. Defaults to False.
            debug_parser_layout: Enable parser layout debugging. Defaults to False.

        Raises:
            FileNotFoundError: If the <knitout.pg> grammar file cannot be located in the package.
        """
        try:
            pg_resource_stream = files(knitout_interpreter.knitout_language).joinpath("knitout.pg")
            self._grammar: Grammar = Grammar.from_file(pg_resource_stream, debug=debug_grammar, ignore_case=True)
        except (FileNotFoundError, AttributeError) as e:
            raise FileNotFoundError(
                f"Could not locate 'knitout.pg' in package 'knitout_interpreter.knitout_language'. "
                f"Please ensure the package is properly installed and the grammar file is included. "
                f"Original error: {e}"
            ) from e
        self._grammar: Grammar = Grammar.from_file(pg_resource_stream, debug=debug_grammar, ignore_case=True)
        self._set_parser(debug_parser, debug_parser_layout)

    def _set_parser(self, debug_parser: bool, debug_parser_layout: bool) -> None:
        """Set up the parser with the current grammar and debugging options.

        Args:
            debug_parser: Enable parser debugging.
            debug_parser_layout: Enable parser layout debugging.
        """
        self._parser: Parser = Parser(self._grammar, debug=debug_parser, debug_layout=debug_parser_layout, actions=action.all)
        self._parser.knitout_parser = self  # make this structure available from actions

    def parse_knitout_to_instructions(
        self,
        pattern: str,
        pattern_is_file: bool = False,
        reset_parser: bool = True,
        debug_parser: bool = False,
        debug_parser_layout: bool = False,
    ) -> list[Knitout_Line]:
        """Parse knitout pattern into a list of instruction objects.

        Args:
            pattern: Either a file path or the knitout string to be parsed.
            pattern_is_file: If True, treat pattern as a file path. Defaults to False.
            reset_parser: Reset parser to have no prior input. Defaults to True.
            debug_parser: Enable parser debugging. Defaults to False.
            debug_parser_layout: Enable parser layout debugging. Defaults to False.

        Returns:
            List of knitout instructions created by parsing the given pattern.

        Raises:
            Knitout_ParseError: If there's an error parsing the knitout code.
            Incomplete_Knitout_Line_Error: If a knitout line processes into an incomplete code.
        """
        codes: list[Knitout_Line] = []
        if reset_parser:
            self._set_parser(debug_parser, debug_parser_layout)
        if pattern_is_file:
            with open(pattern) as pattern_file:
                lines = pattern_file.readlines()
        else:
            lines = pattern.splitlines()
        for i, line in enumerate(lines):
            if not re.match(r"^\s*$", line):
                try:
                    code = self._parser.parse(line)
                except parglare.exceptions.SyntaxError as e:
                    raise Knitout_ParseError(i, line, e) from None
                if code is None:
                    continue
                elif not isinstance(code, Knitout_Line):
                    raise Incomplete_Knitout_Line_Error(i, line) from None
                else:
                    codes.append(code)
        codes_with_no_ops = [self.parse_to_no_op(code) if isinstance(code, Knitout_Comment_Line) else code for code in codes]
        codes_with_bp = [self.parse_to_breakpoint(code) if isinstance(code, Knitout_Comment_Line) else code for code in codes_with_no_ops]
        return codes_with_bp

    @staticmethod
    def parse_to_no_op(comment_line: Knitout_Comment_Line) -> Knitout_Comment_Line | Knitout_No_Op:
        """
        Args:
            comment_line (Knitout_Comment_Line): The comment line to convert to a no-op comment.

        Returns:
            Knitout_Comment_Line | Knitout_No_Op: The no-op line formed from this comment line or the original comment line if it cannot be converted to a no-op comment.
        """
        if comment_line.comment is None or isinstance(comment_line, Knitout_No_Op):
            return comment_line
        index_start = comment_line.comment.find(Knitout_No_Op.NO_OP_TERM)
        if index_start == -1:
            return comment_line
        index_start += len(Knitout_No_Op.NO_OP_TERM)
        lines = parse_knitout(comment_line.comment[index_start:], pattern_is_file=False)
        if len(lines) == 0:
            return comment_line
        else:
            assert len(lines) == 1
            no_op = Knitout_No_Op(lines[0])
            no_op.original_line_number = comment_line.original_line_number
            return no_op

    @staticmethod
    def parse_to_breakpoint(comment_line: Knitout_Comment_Line) -> Knitout_Comment_Line | Knitout_BreakPoint:
        """
        Args:
            comment_line (Knitout_Comment_Line): The comment line to convert to a breakpoint comment.

        Returns:
            Knitout_Comment_Line | Knitout_BreakPoint: The breakpoint line formed from this comment line or the original comment line if it cannot be converted to a breakpoint.
        """
        if comment_line.comment is None or isinstance(comment_line, (Knitout_BreakPoint, Knitout_No_Op)):
            return comment_line
        index_start = comment_line.comment.find(Knitout_BreakPoint.BP_TERM)
        if index_start == -1:
            return comment_line
        index_start += len(Knitout_BreakPoint.BP_TERM)
        bp = Knitout_BreakPoint(comment_line.comment[index_start:])
        bp.original_line_number = comment_line.original_line_number
        return bp


def parse_knitout(pattern: str, pattern_is_file: bool = False, debug_parser: bool = False, debug_parser_layout: bool = False) -> list[Knitout_Line]:
    """Execute the parsing code for the parglare parser.

    This is a convenience function that creates a Knitout_Parser instance
    and parses the given pattern.

    Args:
        pattern: Either a file path or the knitout string to be parsed.
        pattern_is_file: If True, treat pattern as a file path. Defaults to False.
        debug_parser: Enable parser debugging. Defaults to False.
        debug_parser_layout: Enable parser layout debugging. Defaults to False.

    Returns:
        List of knitout instructions created by parsing the given pattern.

    Raises:
        FileNotFoundError: If the grammar file or input file cannot be found.
    """
    parser = Knitout_Parser(debug_parser, debug_parser_layout)
    return parser.parse_knitout_to_instructions(pattern, pattern_is_file, reset_parser=False)
