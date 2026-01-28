from collections.abc import Sequence
from typing import cast

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine_State
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification, Knitting_Machine_Type, Knitting_Position

from knitout_interpreter.knitout_operations.Header_Line import (
    Carriers_Header_Line,
    Gauge_Header_Line,
    Knitout_Header_Line,
    Knitout_Header_Line_Type,
    Knitout_Version_Line,
    Machine_Header_Line,
    Position_Header_Line,
)
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitting_Machine_Header:
    """A class structure for maintaining the relationship between header lines and knitting machine state.

    This class manages the relationship between header lines read from a knitout file  and the state of a given knitting machine.

    """

    def __init__(self, initial_specification: Knitting_Machine_State | Knitting_Machine_Specification | None = None, version: int = 2):
        if initial_specification is None:
            initial_specification = Knitting_Machine_Specification()
        elif not isinstance(initial_specification, Knitting_Machine_Specification):
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
    def specification(self) -> Knitting_Machine_Specification:
        """
        Returns:
            Knitting_Machine_Specification: The knitting machine specification created by this header.
        """
        return Knitting_Machine_Specification(
            machine=cast(Knitting_Machine_Type, self._header_lines[Knitout_Header_Line_Type.Machine].header_value),
            gauge=cast(int, self._header_lines[Knitout_Header_Line_Type.Gauge].header_value),
            position=cast(Knitting_Position, self._header_lines[Knitout_Header_Line_Type.Position].header_value),
            carrier_count=cast(int, self._header_lines[Knitout_Header_Line_Type.Carriers].header_value),
        )

    def set_header_by_specification(self, machine_specification: Knitting_Machine_Specification, version: int = 2) -> None:
        """
        Set the header lines to produce the given machine specification.

        Args:
            machine_specification (Knitting_Machine_Specification): The machine specification to set this header to.
            version (int, optional): The version to set the header to. Defaults to 2.
        """
        self._header_lines = {
            Knitout_Header_Line_Type.Machine: Machine_Header_Line(machine_specification.machine),
            Knitout_Header_Line_Type.Gauge: Gauge_Header_Line(machine_specification.gauge),
            Knitout_Header_Line_Type.Position: Position_Header_Line(machine_specification.position),
            Knitout_Header_Line_Type.Carriers: Carriers_Header_Line(machine_specification.carrier_count),
            Knitout_Header_Line_Type.Knitout_Version: Knitout_Version_Line(version),
        }

    def extract_header(self, instructions: Sequence[Knitout_Line]) -> bool:
        """
        Update the header specification with any header lines in the given instruction sequence.

        Args:
            instructions (Sequence[Knitout_Line]): The instruction sequence of the knitting machine being executed and update the header specification.

        Returns:
            bool: True if any of the headers found in the instruction sequence updated the header specification, False otherwise.
        """
        return any(self._update_header(l) for l in instructions if isinstance(l, Knitout_Header_Line))

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
