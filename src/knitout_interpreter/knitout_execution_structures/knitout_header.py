"""Module containing the Knitting_Machine_Header class"""

from collections.abc import Iterator, Sequence
from typing import cast, overload

from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Type, Knitting_Position

from knitout_interpreter.knitout_execution_structures.Knitout_Knitting_Machine import Knitout_Knitting_Machine, Knitout_Machine_Specification
from knitout_interpreter.knitout_execution_structures.knitout_loops import Knitout_Loop
from knitout_interpreter.knitout_execution_structures.knitout_program import Knitout_Program
from knitout_interpreter.knitout_operations.Header_Line import (
    Carriers_Header_Line,
    Gauge_Header_Line,
    Knitout_Header_Line,
    Knitout_Header_Line_Type,
    Knitout_Version_Line,
    Machine_Header_Line,
    Position_Header_Line,
)


class Knitting_Machine_Header(Sequence[Knitout_Header_Line]):
    """A class structure for maintaining the relationship between header lines and knitting machine state.

    This class manages the relationship between header lines read from a knitout file  and the state of a given knitting machine.

    """

    def __init__(self, initial_specification: Knitout_Knitting_Machine | Knitout_Machine_Specification | None = None, version: int = 2):
        if initial_specification is None:
            initial_specification = Knitout_Machine_Specification()
        elif not isinstance(initial_specification, Knitout_Machine_Specification):
            initial_specification = initial_specification.machine_specification
        self._header_lines: dict[Knitout_Header_Line_Type, Knitout_Header_Line] = {}
        self.set_header_by_specification(initial_specification, version)

    @property
    def header_lines(self) -> list[Knitout_Header_Line]:
        """
        Returns:
            list[Knitout_Header_Line]: A list of Knitout_Header_Lines that are set by this header object.
        """
        return list(self._header_lines.values())

    @property
    def header_len(self) -> int:
        """
        Returns:
            int: The number of lines that will be in this header.
        """
        return len(self._header_lines)

    @property
    def specification(self) -> Knitout_Machine_Specification:
        """
        Returns:
            Knitout_Machine_Specification: The knitting machine specification created by this header.
        """
        return Knitout_Machine_Specification(
            machine=cast(Knitting_Machine_Type, self._header_lines[Knitout_Header_Line_Type.Machine].header_value),
            gauge=cast(int, self._header_lines[Knitout_Header_Line_Type.Gauge].header_value),
            position=cast(Knitting_Position, self._header_lines[Knitout_Header_Line_Type.Position].header_value),
            carrier_count=cast(int, self._header_lines[Knitout_Header_Line_Type.Carriers].header_value),
            loop_class=Knitout_Loop,
        )

    def set_header_by_specification(self, machine_specification: Knitout_Machine_Specification, version: int = 2) -> None:
        """
        Set the header lines to produce the given machine specification.

        Args:
            machine_specification (Knitout_Machine_Specification): The machine specification to set this header to.
            version (int, optional): The version to set the header to. Defaults to 2.
        """
        self._header_lines = {
            Knitout_Header_Line_Type.Machine: Machine_Header_Line(machine_specification.machine),
            Knitout_Header_Line_Type.Gauge: Gauge_Header_Line(machine_specification.gauge),
            Knitout_Header_Line_Type.Position: Position_Header_Line(machine_specification.position),
            Knitout_Header_Line_Type.Carriers: Carriers_Header_Line(machine_specification.carrier_count),
            Knitout_Header_Line_Type.Knitout_Version: Knitout_Version_Line(version),
        }

    def extract_header(self, program: Knitout_Program) -> bool:
        """
        Update the header specification with any header lines in the given instruction sequence.

        Args:
            program (Sequence[Knitout_Line]): The instruction sequence of the knitting machine being executed and update the header specification.

        Returns:
            bool: True if any of the headers found in the instruction sequence updated the header specification, False otherwise.
        """
        return any(self._update_header(l) for l in program.header)

    def _update_header(self, header_line: Knitout_Header_Line) -> bool:
        """Update this header with the given header line.

        Args:
            header_line (Knitout_Header_Line): The header line to update this header with.

        Returns:
            bool: True if this header is updated by the given header line. False, otherwise.
        """
        if header_line.header_type not in self._header_lines:
            self._header_lines[header_line.header_type] = header_line
            return True
        else:
            current_line = self._header_lines[header_line.header_type]
            if header_line != current_line:
                self._header_lines[header_line.header_type] = header_line
                return True
            else:
                return False

    def __iter__(self) -> Iterator[Knitout_Header_Line]:
        return iter(self.header_lines)

    @overload
    def __getitem__(self, index: int) -> Knitout_Header_Line: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Knitout_Header_Line]: ...

    def __getitem__(self, index: object) -> Knitout_Header_Line | Sequence[Knitout_Header_Line]:
        if isinstance(index, (int, slice)):
            return self.header_lines[index]
        else:
            raise TypeError(f"Expected int or slice but got index {index}")

    def __len__(self) -> int:
        return self.header_len
