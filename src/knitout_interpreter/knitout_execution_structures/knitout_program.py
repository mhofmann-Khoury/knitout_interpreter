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
from knitout_interpreter.knitout_operations.needle_instructions import Loop_Making_Instruction, Needle_Instruction
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction


class Knitout_Program(Sequence[Knitout_Line]):
    """
    Class for organizing and maintaining the ordering of knitout lines in a knitout program.
    """

    def __init__(self, lines: Sequence[Knitout_Line], source_program_name: str | None = None, default_version: int = 2) -> None:
        self._source_program: str | None = source_program_name
        self._default_version: int = default_version
        self._original_program: list[Knitout_Line] = [*lines]
        self._program: list[Knitout_Line] = [*self._original_program]
        for i, line in enumerate(self):
            line.set_line(i, self._source_program)
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
    def needle_instructions(self) -> list[Needle_Instruction]:
        """
        Returns:
            list[Needle_Instruction]: The list of instructions that operate on a needle in the body of the program.
        """
        return [i for i in self if isinstance(i, Needle_Instruction)]

    @property
    def loop_forming_instructions(self) -> list[Loop_Making_Instruction]:
        """
        Returns:
            list[Loop_Making_Instruction]: The list of loop forming instructions in the body of the program.
        """
        return [i for i in self if isinstance(i, Loop_Making_Instruction)]

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

    def next_loop_forming_instruction_index(self, index: int) -> int | None:
        """
        Args:
            index (int): The index in the program to search forward form for the next loop forming instruction.

        Returns:
            int | None: Index where the next loop forming instruction is or None if no future loop forming instruction is found.

        Notes:
            Excludes loop forming instruction at the given index.
        """
        return next((i + index for i, line in enumerate(self._program[index + 1 :]) if isinstance(line, Loop_Making_Instruction)), None)

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

    def swap_line(self, line_index: int, new_line: Knitout_Line, new_source: str | None = None) -> None:
        """
        Swaps the line at the given index with the given new line. The line number of the new line is set to its current position, but any original line number or source remain the same.

        Args:
            line_index (int): An index in the program to swap out.
            new_line (Knitout_Line): The new line to swap at the given position.
            new_source (str, optional):
                The source program of the new line.
                Defaults to taking the source name from this program or the source name already defined in the given new_line.
        """
        source = new_source if new_source is not None else self._source_program
        new_line.set_line(self[line_index].line_number, source)
        self[line_index] = new_line

    def insert_line(self, index: int, new_line: Knitout_Line, new_source: str | None = None) -> None:
        """
        Inserts the given line into the program at the given index.

        Args:
            index (int): The index to insert into the program. The new line number for the given new line.
            new_line (Knitout_Line): The line to insert into the program.
            new_source (str, optional): The name of the source program for the new line if it is not already set.
        """
        new_line.set_line(index, new_source)
        self._program.insert(index, new_line)
        self._update_line_numbers()

    def append_line(self, line: Knitout_Line) -> None:
        """
        Add the given line to the end of the program.
        Args:
            line (Knitout_Line): The line to append.
        """
        line.set_line(len(self), self._source_program)
        self._program.append(line)

    def remove_line(self, line_index_to_remove: int) -> Knitout_Line:
        """
        Removes the line at the given index of the program and updates the line numbers of all remaining lines in the program.
        Args:
            line_index_to_remove (int): The index of the knitout line to remove from the program

        Returns:
            Knitout_Line: The removed line from the program.
        """
        line = self._program.pop(line_index_to_remove)
        self._update_line_numbers()
        return line

    def swap_lines(self, start_index: int, new_lines: Sequence[Knitout_Line], new_source: str | None = None) -> None:
        """
        Swaps the lines starting from the given index with the given new line.
        The line number of the new lines are set to their current position, but any original line number or source remain the same.

        Args:
            start_index (int): An index to start swapping lines from.
            new_lines (Sequence[Knitout_Line]): The new lines to swap at the given positions.
            new_source (str, optional):
                The source program of the new lines.
                Defaults to taking the source name from this program or the source name already defined in the given new_lines.
        """
        source = new_source if new_source is not None else self._source_program
        start_line_number = self[start_index].line_number
        for i, new_line in enumerate(new_lines):
            new_line.set_line(start_line_number + i, source)
            self[start_index + 1] = new_line

    def insert_lines(self, start_index: int, new_lines: Sequence[Knitout_Line], new_source: str | None = None) -> None:
        """
        Inserts the given line into the program at the given index.

        Args:
            start_index (int): The index to start inserting into the program.
            new_lines (Sequence[Knitout_Line]): The lines to insert into the program.
            new_source (str, optional): The name of the source program for the new line if it is not already set.
        """
        for i, new_line in enumerate(new_lines):
            new_line.set_line(start_index + i, new_source)
            self._program.insert(start_index + i, new_line)
        self._update_line_numbers()

    def append_lines(self, lines: Sequence[Knitout_Line]) -> None:
        """
        Add the given line to the end of the program.
        Args:
            lines (Knitout_Line): The line to append.
        """
        for line in lines:
            line.set_line(len(self), self._source_program)
            self._program.append(line)

    def remove_lines(self, start_index: int, end_index: int) -> None:
        """
        Removes the lines at the given range of indices of the program and updates the line numbers of all remaining lines in the program.
        Args:
            start_index (int): The starting index of the knitout lines to remove from the program. This index will be removed (inclusive).
            end_index (int): The ending index of the knitout lines to remove from the program. This index will be removed (inclusive).
        """
        del self._program[start_index : end_index + 1]
        self._update_line_numbers()

    def shift_needle_positions(self, delta: int = 0) -> None:
        """
        Sets all needles in the current program to left align to provided needle number.

        Args:
            delta (int, optional): The number by which to offset (+ or -) compared to the original position of the needles. Defaults to 0 with no effect on the program.
        """
        if delta == 0:
            return
        for i, line in enumerate(self):
            if isinstance(line, Needle_Instruction):
                self.swap_line(i, line.shift_needle_position(delta))

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

    def instructions_within_range(self, range_slice: slice) -> list[Knitout_Instruction]:
        """
        Args:
            range_slice (slice): The slice of the program to gather instructions from. These indices include all program lines, not just instructions.

        Returns:
            list[Knitout_Instruction]: The list of instructions within the given range of program indices.
        """
        program_slice = self._program[range_slice]
        return [i for i in program_slice if isinstance(i, Knitout_Instruction)]

    def _update_line_numbers(self) -> None:
        """
        Updates the line number of each instruction in the program to the current ordering of the program.
        """
        for i, line in enumerate(self):
            line.set_line(i)

    def __contains__(self, item: object) -> bool:
        """
        Args:
            item (int | Knitout_Line): The line or line index to check for in the program.

        Returns:
            bool: True if the given index or line is in the program.
        """
        if isinstance(item, int):
            return 0 <= item < len(self)
        elif isinstance(item, Knitout_Line):
            return item in self._program
        return False

    @overload
    def __getitem__(self, index: int) -> Knitout_Line: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Knitout_Line]: ...

    def __getitem__(self, index: object) -> Knitout_Line | Sequence[Knitout_Line]:
        if isinstance(index, (int, slice)):
            return self._program[index]
        else:
            raise TypeError(f"Index {index} is not an integer or slice.")

    def __setitem__(self, key: int, value: Knitout_Line) -> None:
        self._program[key] = value

    def __len__(self) -> int:
        return len(self._program)

    def __iter__(self) -> Iterator[Knitout_Line]:
        return iter(self._program)
