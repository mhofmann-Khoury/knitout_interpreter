"""Module used to manage the context of a knitout interpreter."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.Header_Line import Knitout_Header_Line, Knitout_Version_Line, Knitting_Machine_Header
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line, Knitout_Line


def process_knitout_instructions(
    knitout_lines: Sequence[Knitout_Line],
) -> tuple[Knitout_Version_Line, list[Knitout_Header_Line], list[Knitout_Instruction], list[Knitout_Comment_Line]]:
    """Separate list of knitout codes into components of a program for execution.

    Args:
        knitout_lines (list[Knitout_Line]): The knitout instructions to separate into program components.

    Returns:
        tuple[Knitout_Version_Line, list[Knitout_Header_Line], list[Knitout_Instruction], list[Knitout_Comment_Line]]:
            * Version line for the knitout program
            * List of header lines
            * List of instruction lines
            * List of comment lines
    """
    version_line: Knitout_Version_Line = Knitout_Version_Line()
    head: list[Knitout_Header_Line] = []
    instructions: list[Knitout_Instruction] = []
    comments: list[Knitout_Comment_Line] = []
    for knitout_line in knitout_lines:
        if isinstance(knitout_line, Knitout_Version_Line):
            version_line = knitout_line
        elif isinstance(knitout_line, Knitout_Header_Line):
            head.append(knitout_line)
        elif isinstance(knitout_line, Knitout_Instruction):
            instructions.append(knitout_line)
        else:
            comments.append(cast(Knitout_Comment_Line, knitout_line))
    return version_line, head, instructions, comments


class Knitout_Context:
    """Maintains information about the state of a knitting process as knitout instructions are executed.

    Attributes:
        machine_state (Knitting_Machine): State of the knitting machine that the context is executing on.
        executed_header (list[Knitout_Header_Line]): The ordered list of header lines that have been executed in this context.
        executed_instructions (list[Knitout_Instruction]): The ordered list of instructions executed in this context.
    """

    def __init__(self) -> None:
        self.machine_state: Knitting_Machine = Knitting_Machine()
        self._version_line: Knitout_Version_Line | None = None
        self.executed_header: Knitting_Machine_Header = Knitting_Machine_Header(self.machine_state.machine_specification)
        self.executed_instructions: list[Knitout_Instruction] = []

    @property
    def version(self) -> int:
        """Get the knitout version of the current context.

        Returns:
            int: The knitout version number, defaults to 2 if no version is set.
        """
        if self._version_line is not None:
            return int(self._version_line.version)
        else:
            return 2

    @version.setter
    def version(self, version_line: Knitout_Version_Line | int) -> None:
        """Set the version line for the current context.

        This will override any existing version.

        Args:
            version_line (Knitout_Version_Line | int): The version line to set for this context.
        """
        if isinstance(version_line, int):
            version_line = Knitout_Version_Line(version_line)
        self._version_line = version_line

    def execute_header(self, header_declarations: Sequence[Knitout_Header_Line]) -> None:
        """
        Update the machine state based on the given header values.
        Header declarations that do not change the current context can optionally be converted to comments.

        Args:
            header_declarations (Sequence[Knitout_Header_Line]): The header lines to update based on.
        """
        for header_line in header_declarations:
            updated = self.executed_header.update_header(header_line, update_machine=True)  # update process will always yield a complete header
            if updated:
                self.machine_state = Knitting_Machine(machine_specification=self.machine_state.machine_specification)

    def execute_instructions(self, instructions: Sequence[Knitout_Line]) -> None:
        """Execute the instruction set on the machine state defined by the current header.

        Args:
            instructions (Sequence[Knitout_Line]): Instructions to execute on the knitting machine.
        """
        execution = Knitout_Executer(knitout_program=instructions, knitting_machine=self.machine_state, knitout_version=self.version)
        self.executed_instructions = cast(list[Knitout_Instruction], execution.executed_instructions)

    def execute_knitout(
        self,
        version_line: Knitout_Version_Line,
        header_declarations: list[Knitout_Header_Line],
        instructions: Sequence[Knitout_Instruction],
    ) -> tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
        """Execute the given knitout organized by version, header, and instructions.

        Args:
            version_line (Knitout_Version_Line): The version of knitout to use.
            header_declarations (list[Knitout_Header_Line]): The header to define the knitout file.
            instructions (Sequence[Knitout_Instruction]): The instructions to execute on the machine.

        Returns:
            tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
                A tuple containing:
                    - List of knitout instructions that were executed
                    - Machine state after execution
                    - Knit graph created by execution
        """
        self.version = version_line
        self.execute_header(header_declarations)
        self.execute_instructions(instructions)
        for i, instruction in enumerate(self.executed_instructions):
            instruction.original_line_number = i
        return (
            self.executed_instructions,
            self.machine_state,
            self.machine_state.knit_graph,
        )

    def process_knitout_file(self, knitout_file_name: str) -> tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
        """Parse and process a file of knitout code.

        Args:
            knitout_file_name (str): File path containing knitout code to process.

        Returns:
            tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
                A tuple containing:
                    - List of knitout instructions that were executed
                    - Machine state after execution
                    - Knit graph created by execution
        """
        codes = parse_knitout(knitout_file_name, pattern_is_file=True, debug_parser=False, debug_parser_layout=False)
        return self.execute_knitout_instructions(codes)

    def execute_knitout_instructions(self, codes: Sequence[Knitout_Line]) -> tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
        """Execute given knitout instructions.

        Args:
            codes (list[Knitout_Line]): List of knitout lines to execute.

        Returns:
            tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
                A tuple containing:
                    - List of executed knitout lines
                    - Machine state after execution
                    - Knit graph created by execution
        """
        version, head, instructions, comments = process_knitout_instructions(codes)
        return self.execute_knitout(version, head, instructions)
