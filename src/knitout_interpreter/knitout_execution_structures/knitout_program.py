"""
Module containing the Knitout_Program class for organizing and maintaining the indices of knitout instructions.
"""

from __future__ import annotations

import copy
from collections.abc import Iterator, Sequence
from typing import overload

from knitout_interpreter.knitout_operations.Header_Line import Knitout_Header_Line, Knitout_Version_Line
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_BreakPoint, Knitout_Comment_Line, Knitout_Line, Knitout_No_Op
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction


class Knitout_Program(Sequence[Knitout_Line]):
    """
    Class for organizing and maintaining the ordering of knitout lines in a knitout program.
    """

    def __init__(self, lines: Sequence[Knitout_Line], default_version: int = 2) -> None:
        self._default_version: int = default_version
        self._original_program: list[Knitout_Line] = [*lines]
        self._program: list[Knitout_Line] = [*self._original_program]
        for i, line in enumerate(self):
            line.original_line_number = i
            line.line_number = i
        self._instruction_after_breakpoint: dict[int, Knitout_Instruction] = {}
        for i, line in enumerate(lines):
            if isinstance(line, Knitout_BreakPoint):
                next_instruction = next((next_line for next_line in self._original_program[i + 1 :] if isinstance(next_line, Knitout_Instruction)), None)
                if isinstance(next_instruction, Knitout_Instruction):
                    assert next_instruction.original_line_number is not None
                    self._instruction_after_breakpoint[next_instruction.original_line_number] = next_instruction

    @property
    def header(self) -> list[Knitout_Header_Line]:
        """
        Returns:
            list[Knitout_Header_Line]: The list of header lines in the program.
        """
        return [i for i in self if isinstance(i, Knitout_Header_Line)]

    @property
    def program_body(self) -> list[Knitout_Instruction | Knitout_Comment_Line]:
        """
        Returns:
            list[Knitout_Instruction | Knitout_Comment_Line]: The list of instructions and comments in the body of the program.
        """
        return [i for i in self if isinstance(i, (Knitout_Instruction, Knitout_Comment_Line))]

    @property
    def instructions(self) -> list[Knitout_Instruction]:
        """
        Returns:
            list[Knitout_Instruction]: The list of instructions in the body of the program.
        """
        return [i for i in self if isinstance(i, Knitout_Instruction)]

    @property
    def comments(self) -> list[Knitout_Comment_Line]:
        """
        Returns:
            list[Knitout_Comment_Line]: The list of comment lines in the program. Excludes breakpoints.
        """
        return [i for i in self if isinstance(i, Knitout_Comment_Line) and not isinstance(i, Knitout_BreakPoint)]

    @property
    def version_line(self) -> Knitout_Version_Line:
        """
        Returns:
            Knitout_Version_Line: Knitout_Version_Line for the program.
        """
        return next((i for i in self if isinstance(i, Knitout_Version_Line)), Knitout_Version_Line(self._default_version, comment="Default Version Line"))

    def instruction_pauses_after_breakpoint(self, instruction: Knitout_Instruction) -> bool:
        """
        Args:
            instruction (Knitout_Instruction): The instruction to pause.

        Returns:
            bool: True if the given instruction follows a breakpoint in the original program.
        """
        return instruction.original_line_number in self._instruction_after_breakpoint

    def new_program(self) -> Knitout_Program:
        """
        Returns:
            Knitout_Program: A knitout program initiated to the current state of the program.
        """
        return Knitout_Program([copy.deepcopy(i) for i in self])

    def new_header_program(self) -> Knitout_Program:
        """
        Returns:
            Knitout_Program: A knitout program copied from the version and header lines of this program.
        """
        program: list[Knitout_Line] = []
        program.extend(copy.deepcopy(h) for h in self.header)
        if not any(isinstance(i, Knitout_Version_Line) for i in program):
            program.insert(0, copy.deepcopy(self.version_line))
        return Knitout_Program(program)

    def append(self, line: Knitout_Line) -> None:
        """
        Add the given line to the end of the program.
        Args:
            line (Knitout_Line): The line to append.
        """
        line.original_line_number = len(self)
        line.line_number = len(self)
        self._program.append(line)

    def organize_program(self, remove_comments: bool = True, remove_no_op: bool = True, remove_pause: bool = True, remove_breakpoint: bool = True) -> None:
        """
        Organizes the program to a standard ordering (version line, header, knitout program).
        Args:
            remove_comments (bool, optional): If True, excludes all comments from the program.
            remove_no_op (bool, optional): If True, excludes all no-op operation from the program.
            remove_pause (bool, optional): If True, excludes all pause operations from the program.
            remove_breakpoint (bool, optional): If True, excludes all breakpoints from the program.
        """
        body = self.instructions if remove_comments else self.program_body
        organized_program: list[Knitout_Line] = [self.version_line, *self.header, *body]
        if not remove_comments and remove_no_op:
            organized_program = [i for i in organized_program if not isinstance(i, Knitout_No_Op)]
        if remove_breakpoint:
            organized_program = [i for i in organized_program if not isinstance(i, Knitout_BreakPoint)]
        if remove_pause:
            organized_program = [i for i in organized_program if not isinstance(i, Pause_Instruction)]
        self._program = organized_program
        self._update_line_numbers()

    def _update_line_numbers(self) -> None:
        """
        Updates the line number of each instruction in the program to the current ordering of the program.
        """
        for i, line in enumerate(self):
            line.line_number = i

    @overload
    def __getitem__(self, index: int) -> Knitout_Line: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Knitout_Line]: ...

    def __getitem__(self, index: object) -> Knitout_Line | Sequence[Knitout_Line]:
        if isinstance(index, (int, slice)):
            return self._program[index]
        else:
            raise TypeError(f"Index {index} is not an integer or slice.")

    def __len__(self) -> int:
        return len(self._program)

    def __iter__(self) -> Iterator[Knitout_Line]:
        return iter(self._program)
