"""Exceptions related to processing knitout"""

from __future__ import annotations

from typing import TYPE_CHECKING

import parglare

if TYPE_CHECKING:
    from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Error(Exception):
    """
    An super type for exceptions related to execution a knitout program.
    """

    def __init__(self, message: str) -> None:
        """Initialize a knitout exception with formatted message.

        Args:
            message (str): The descriptive error message about knitout error
        """
        self.message = f"{self.__class__.__name__}: {message}"
        super().__init__(self.message)


class Knitout_ParseError(Knitout_Error):
    """Raised from a knitout file with a parsing error"""

    def __init__(self, line_number: int, knitout_line: str, parse_error: parglare.exceptions.SyntaxError) -> None:
        self.line_number: int = line_number
        self.knitout_line: str = knitout_line
        self.parse_error: parglare.exceptions.SyntaxError = parse_error
        super().__init__(f"line {line_number} <{str(knitout_line).strip()}>:\n\t{parse_error.context_message}")


class Incomplete_Knitout_Line_Error(Knitout_Error):
    """Raised from a knitout file when parsing an incomplete knitout line"""

    def __init__(self, line_number: int, knitout_line: str) -> None:
        self.line_number: int = line_number
        self.knitout_line: str = knitout_line
        super().__init__(f"line {line_number} <{knitout_line}> did not produce a complete knitout line")


class Knitout_Machine_StateError(Knitout_Error):
    """Raised when executing a line of knitout caused an error"""

    def __init__(self, knitout_line: Knitout_Line, error: Exception, line_number: int | None = None) -> None:
        """
        Args:
            knitout_line (Knitout_Line): The knitout line being executed that caused the error.
            error (Exception): An exception raised during the execution of a knitout program.
            line_number (int, optional): The line number of the instruction. Defaults to the original line number of the given knitout line.
        """
        if line_number is None:
            line_number = knitout_line.original_line_number
        self.line_number: int | None = line_number
        self.knitout_line: Knitout_Line = knitout_line
        self.error: Exception = error
        message = f"\nline {self.line_number}: {self.knitout_line}:\n\t{error}" if self.line_number is not None else f"\n{self.knitout_line}:\n\t{error}"
        super().__init__(message)
