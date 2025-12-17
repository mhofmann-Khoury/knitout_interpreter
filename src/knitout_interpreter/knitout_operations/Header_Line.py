"""Module containing the classes for Header Lines in Knitout"""

import warnings
from collections.abc import Sequence
from enum import Enum
from typing import Any, cast

from knit_graphs.Yarn import Yarn_Properties
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification, Knitting_Machine_Type, Knitting_Position
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter._warning_stack_level_helper import get_user_warning_stack_level_from_knitout_interpreter_package
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Header_Line_Type(Enum):
    """Enumeration of properties that can be set in the header."""

    Machine = "Machine"  # Denotes the type of machine to build
    Gauge = "Gauge"  # Denotes the needles per inch of the machine
    Yarn = "Yarn"  # Sets a specific yarn on a specified carrier.
    Position = "Position"  # Denotes the position of the knitting pattern on the needle beds.
    Carriers = "Carriers"  # Denotes the carriers on the machine.
    Knitout_Version = "Knitout_Version"  # Denotes the knitout version expected in the program.

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class Knitout_Header_Line(Knitout_Line):

    def __init__(self, header_type: Knitout_Header_Line_Type, header_value: Any, comment: str | None = None):
        """
        Args:
            header_type (Knitout_Header_Line_Type): The type of value set by this header line.
            header_value (Any): The value set by this header line.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        super().__init__(comment)
        self._header_value: Any = header_value
        self._header_type: Knitout_Header_Line_Type = header_type

    @property
    def header_type(self) -> Knitout_Header_Line_Type:
        """
        Returns:
            Knitout_Header_Line_Type: The type of value to be changed by this header line.
        """
        return self._header_type

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """Check if this header would update the given machine state.

        Args:
            machine_state (Knitting_Machine): The machine state to check against.

        Returns:
            True if this header would update the given machine state, False otherwise.
        """
        return False

    def __str__(self) -> str:
        return f";;{self.header_type}: {self._header_value}{self.comment_str}"


class Knitout_Version_Line(Knitout_Header_Line):
    """Represents a knitout version specification line."""

    def __init__(self, version: int = 2, comment: None | str = None):
        """Initialize a version line.

        Args:
            version (int, optional): The knitout version number. Defaults to 2.
            comment (str, optional): Optional comment for the version line.
        """
        super().__init__(Knitout_Header_Line_Type.Knitout_Version, version, comment)

    @property
    def version(self) -> int:
        """
        Returns:
            int: The version of knitout to use in the program.
        """
        return int(self._header_value)

    def __str__(self) -> str:
        return f";!knitout-{self.version}{self.comment_str}"


class Machine_Header_Line(Knitout_Header_Line):

    def __init__(self, machine_type: str, comment: str | None = None):
        """
        Args:
            machine_type (str): The name of the type of machine the knitout should be executed on.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        super().__init__(Knitout_Header_Line_Type.Machine, Knitting_Machine_Type[machine_type], comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return bool(self._header_value != machine_state.machine_specification.machine)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.machine_specification.machine = self._header_value
            return True
        else:
            return False


class Gauge_Header_Line(Knitout_Header_Line):

    def __init__(self, gauge: int, comment: str | None = None):
        """

        Args:
            gauge (int): The number of needles per inch on the knitting machine.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        super().__init__(Knitout_Header_Line_Type.Gauge, gauge, comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return bool(self._header_value != machine_state.machine_specification.gauge)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.machine_specification.gauge = self._header_value
            return True
        else:
            return False


class Position_Header_Line(Knitout_Header_Line):

    def __init__(self, position: str | Knitting_Position, comment: str | None = None):
        """
        Args:
            position (str | Knitting_Position): Indicates the position of the knitting area on the needle beds.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        if isinstance(position, str):
            position = Knitting_Position[position]
        super().__init__(Knitout_Header_Line_Type.Position, position, comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return bool(self._header_value != machine_state.machine_specification.position)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.machine_specification.position = self._header_value
            return True
        else:
            return False


class Yarn_Header_Line(Knitout_Header_Line):
    def __init__(self, carrier_id: int, plies: int, yarn_weight: float, color: str, comment: str | None = None):
        """

        Args:
            carrier_id (int): The id of the yarn-carrier being assigned a yarn value.
            plies (int): The number of plies being assigned a yarn value.
            yarn_weight (float): The weight of the yarn being assigned a yarn value.
            color (str): The color of the yarn being assigned a yarn value.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        self._yarn_properties: Yarn_Properties = Yarn_Properties(f"carrier+{carrier_id}_yarn", plies, yarn_weight, color)
        self._carrier_id: int = carrier_id
        super().__init__(Knitout_Header_Line_Type.Yarn, self._yarn_properties, comment)

    def __str__(self) -> str:
        return f";;{self.header_type}-{self._carrier_id}: {self._yarn_properties.plies}-{self._yarn_properties.weight} {self._yarn_properties.color}{self.comment_str}"

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return bool(self._yarn_properties != machine_state.carrier_system[self._carrier_id].yarn.properties)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.carrier_system[self._carrier_id].yarn.properties = self._yarn_properties
            return True
        else:
            return False


class Carriers_Header_Line(Knitout_Header_Line):

    def __init__(self, carrier_ids: list[int] | int | Yarn_Carrier_Set | Yarn_Carrier, comment: str | None = None):
        """
        Args:
            carrier_ids (list[int] | int | Yarn_Carrier_Set | Yarn_Carrier): Indicates the carriers available on the knitting machine when executing the knitting program.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        if isinstance(carrier_ids, int):
            carrier_ids = Yarn_Carrier_Set([i + 1 for i in range(carrier_ids)])
        elif isinstance(carrier_ids, Yarn_Carrier):
            carrier_ids = Yarn_Carrier_Set([carrier_ids.carrier_id])
        elif isinstance(carrier_ids, list):
            carrier_ids = Yarn_Carrier_Set(cast(list[int | Yarn_Carrier], carrier_ids))
        super().__init__(Knitout_Header_Line_Type.Carriers, carrier_ids, comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return len(machine_state.carrier_system.carriers) != len(self._header_value)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        carrier_count = len(self._header_value)
        if self.updates_machine_state(machine_state):
            machine_state.machine_specification.carrier_count = carrier_count
            return True
        return False


class Ignored_Header_Warning(Knitting_Machine_Warning):
    """Warning that indicates that a portion of a knitout header was ignored because it was executed when the machine was active and couldn't be changed."""

    def __init__(self, header_line: Knitout_Header_Line):
        """
        Args:
            header_line (Knitout_Header_Line): The header line that will be ignored.
        """
        super().__init__(message=f"Ignored Header Updates Active Machine: {header_line}".rstrip(), ignore_instructions=True)


class Knitting_Machine_Header:
    """A class structure for maintaining the relationship between header lines and knitting machine state.

    This class manages the relationship between header lines read from a knitout file
    and the state of a given knitting machine.

    Attributes:
        specification (Knitting_Machine_Specification): The specification of the knitting machine created by this header.
    """

    def __init__(self, initial_specification: Knitting_Machine_Specification | None = None):
        if initial_specification is None:
            initial_specification = Knitting_Machine_Specification()
        self.specification: Knitting_Machine_Specification = initial_specification
        self._header_lines: dict[Knitout_Header_Line_Type, Knitout_Header_Line] = {}
        self.set_header_by_specification(self.specification)

    @property
    def header_len(self) -> int:
        """
        Returns:
            int: The number of lines that will be in this header, including the version line.
        """
        return 1 + len(self._header_lines)

    @property
    def machine(self) -> Knitting_Machine:
        """
        Returns:
            Knitting_Machine: A new knitting machine that is configured by this header's specification.
        """
        return Knitting_Machine(self.specification)

    def extract_header(self, instructions: Sequence[Knitout_Line]) -> bool:
        """
        Update the header specification with any header lines in the given instruction sequence.

        Args:
            instructions (Sequence[Knitout_Line]): The instruction sequence of the knitting machine being executed and update the header specification.

        Returns:
            bool: True if any of the headers found in the instruction sequence updated the header specification, False otherwise.
        """
        return any(self.update_header(l, update_machine=True) for l in instructions if isinstance(l, Knitout_Header_Line))

    def update_header(self, header_line: Knitout_Header_Line, update_machine: bool = False) -> bool:
        """Update this header with the given header line.

        Args:
            header_line (Knitout_Header_Line): The header line to update this header with.
            update_machine (bool, optional):
                If True, the header line will update the machine state to the new values in this header_line, if present.
                If False, the header line will only update this header if there is no explicitly set header line for that value.

        Returns:
            bool: True if this header is updated by the given header line. False, otherwise.

        Warns:
            Ignored_Header_Warning: If the header line is ignored because it updates the machine state after the machine is already active.

        Note:
            If update_machine is False, no updates are allowed and this will always return False.
        """
        self._header_lines[header_line.header_type] = header_line
        if update_machine:  # update the machine state and then add this to the header if it caused an update
            updated = header_line.execute(self.machine)
            if updated:
                self._header_lines[header_line.header_type] = header_line
                self.specification = self.machine.machine_specification
                return True
            else:
                return False
        else:
            would_update = header_line.updates_machine_state(self.machine)
            if would_update:
                warnings.warn(
                    Ignored_Header_Warning(header_line),
                    stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package(),
                )
            return False

    def set_header_by_specification(self, machine_specification: Knitting_Machine_Specification) -> None:
        """
        Set the header lines to produce the given machine specification.

        Args:
            machine_specification (Knitting_Machine_Specification): The machine specification to set this header to.
        """
        self._header_lines = {
            Knitout_Header_Line_Type.Machine: Machine_Header_Line(str(machine_specification.machine)),
            Knitout_Header_Line_Type.Gauge: Gauge_Header_Line(machine_specification.gauge),
            Knitout_Header_Line_Type.Position: Position_Header_Line(str(machine_specification.position)),
            Knitout_Header_Line_Type.Carriers: Carriers_Header_Line(machine_specification.carrier_count),
        }

    def get_header_lines(self, version: int = 2) -> list[Knitout_Header_Line]:
        """Get a complete knitout header from the stored header lines.

        Args:
            version (int, optional): The knitout version number to process with. Defaults to 2.

        Returns:
            list[Knitout_Header_Line]: List of header lines that form a complete knitout header. This starts with a version line.
        """
        values: list[Knitout_Header_Line] = [Knitout_Version_Line(version)]
        values.extend(self._header_lines.values())
        return values


def get_machine_header(knitting_machine: Knitting_Machine, version: int = 2) -> list[Knitout_Header_Line]:
    """Get a list of header lines that describe the given machine state.

    Args:
        knitting_machine (Knitting_Machine): The machine state to specify as a header.
        version (int, optional): The desired knitout version of the header. Defaults to 2.

    Returns:
        list[Knitout_Line]: A list containing header lines and a version line that describes the given machine state.
    """
    header = Knitting_Machine_Header(knitting_machine.machine_specification)
    return header.get_header_lines(version)
