"""Module containing the classes for Header Lines in Knitout"""

from collections.abc import Sequence
from enum import Enum

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification, Knitting_Machine_Type, Knitting_Position
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier

from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Header_Line_Type(Enum):
    """Enumeration of properties that can be set in the header."""

    Machine = "machine"  # Denotes the type of machine to build.
    Gauge = "gauge"  # Denotes the needles per inch of the machine.
    Position = "position"  # Denotes the position of the knitting pattern on the needle beds.
    Carriers = "carrier_count"  # Denotes the carriers on the machine.
    Knitout_Version = "version"  # Denotes the knitout version expected in the program.

    def get_specification_value(self, specification: Knitting_Machine_Specification) -> Knitting_Machine_Type | int | Knitting_Position:
        """
        Args:
            specification (Knitting_Machine_Specification): The specification to retrieve the value associated with this header line type.

        Returns:
            Knitting_Machine_Type | int | Knitting_Position:
                Return the value in the specification associated with this header type.
        """
        if self is Knitout_Header_Line_Type.Machine:
            return specification.machine
        elif self is Knitout_Header_Line_Type.Gauge:
            return specification.gauge
        elif self is Knitout_Header_Line_Type.Position:
            return specification.position
        elif self is Knitout_Header_Line_Type.Carriers:
            return specification.carrier_count
        else:  # if self is Knitout_Header_Line_Type.Knitout_Version:
            return 2

    @property
    def specification_keyword(self) -> str:
        """
        Returns:
            str: The keyword to initialize this value in a Knitting_Machine_Specification.
        """
        return self.value

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


class Knitout_Header_Line(Knitout_Line):

    def __init__(self, header_type: Knitout_Header_Line_Type, header_value: Knitting_Machine_Type | int | Knitting_Position, comment: str | None = None):
        """
        Args:
            header_type (Knitout_Header_Line_Type): The type of value set by this header line.
            header_value (Knitting_Machine_Type | int | Knitting_Position): The value set by this header line.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        super().__init__(comment)
        self._header_value: Knitting_Machine_Type | int | Knitting_Position = header_value
        self._header_type: Knitout_Header_Line_Type = header_type

    @property
    def header_type(self) -> Knitout_Header_Line_Type:
        """
        Returns:
            Knitout_Header_Line_Type: The type of value to be changed by this header line.
        """
        return self._header_type

    @property
    def header_value(self) -> Knitting_Machine_Type | int | Knitting_Position:
        """
        Returns:
            Knitting_Machine_Type | int | Knitting_Position: The value set by this header line.
        """
        return self._header_value

    def value_matches_spec(self, specification: Knitting_Machine_Specification) -> bool:
        """
        Args:
            specification (Knitting_Machine_Specification): The machine specification to compare this header line to.

        Returns:
            bool: True if the given header value matches the value in the given specification.
        """
        spec_value = self.header_type.get_specification_value(specification)
        return spec_value == self._header_value

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """Check if this header would update the given machine state.

        Args:
            machine_state (Knitting_Machine): The machine state to check against.

        Returns:
            True if this header would update the given machine state, False otherwise.
        """
        return self.value_matches_spec(machine_state.machine_specification)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        return self.updates_machine_state(machine_state)

    def __str__(self) -> str:
        return f";;{self.header_type}: {self._header_value}{self.comment_str}"

    def __eq__(self, other: object) -> bool:
        """
        Args:
            other (Knitout_Header_Line): The other header line to compare to.

        Returns:
            bool: True if other is of the same type and share the same header values.
        """
        return isinstance(other, type(self)) and other.header_type == self.header_type and other._header_value == self._header_value


class Knitout_Version_Line(Knitout_Header_Line):
    """Represents a knitout version specification line."""

    def __init__(self, version: int = 2, comment: None | str = None):
        """Initialize a version line.

        Args:
            version (int, optional): The knitout version number. Defaults to 2.
            comment (str, optional): Optional comment for the version line.
        """
        self._version: int = version
        super().__init__(Knitout_Header_Line_Type.Knitout_Version, version, comment)

    @property
    def version(self) -> int:
        """
        Returns:
            int: The version of knitout to use in the program.
        """
        return self._version

    def __str__(self) -> str:
        return f";!knitout-{self.version}{self.comment_str}"


class Machine_Header_Line(Knitout_Header_Line):

    def __init__(self, machine_type: str | Knitting_Machine_Type, comment: str | None = None):
        """
        Args:
            machine_type (str): The name of the type of machine the knitout should be executed on.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        self._machine: Knitting_Machine_Type = Knitting_Machine_Type[machine_type] if isinstance(machine_type, str) else machine_type
        super().__init__(Knitout_Header_Line_Type.Machine, self._machine, comment)

    @property
    def machine_type(self) -> Knitting_Machine_Type:
        """
        Returns:
            Knitting_Machine_Type: The type of machine the header line is set to.
        """
        return self._machine


class Gauge_Header_Line(Knitout_Header_Line):

    def __init__(self, gauge: int, comment: str | None = None):
        """

        Args:
            gauge (int): The number of needles per inch on the knitting machine.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        self._gauge: int = gauge
        super().__init__(Knitout_Header_Line_Type.Gauge, gauge, comment)

    @property
    def gauge(self) -> int:
        """
        Returns:
            int: The Gauge value set by this header line.
        """
        return self._gauge


class Position_Header_Line(Knitout_Header_Line):

    def __init__(self, position: str | Knitting_Position, comment: str | None = None):
        """
        Args:
            position (str | Knitting_Position): Indicates the position of the knitting area on the needle beds.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """

        self._position: Knitting_Position = Knitting_Position[position] if isinstance(position, str) else position
        super().__init__(Knitout_Header_Line_Type.Position, self._position, comment)

    @property
    def position(self) -> Knitting_Position:
        """
        Returns:
            Knitting_Position: The position of the knitting area on the needle beds.
        """
        return self._position


class Carriers_Header_Line(Knitout_Header_Line):

    def __init__(self, carrier_ids: Sequence[int | Yarn_Carrier] | Sequence[int] | Sequence[Yarn_Carrier] | int | Yarn_Carrier = 10, comment: str | None = None):
        """
        Args:
            carrier_ids (list[int] | int | Yarn_Carrier_Set | Yarn_Carrier): Indicates the carriers available on the knitting machine when executing the knitting program.
            comment (str, optional): Additional details in the comments. Defaults to no comment.
        """
        if isinstance(carrier_ids, int):
            self._carrier_count: int = carrier_ids
        elif isinstance(carrier_ids, Yarn_Carrier):
            self._carrier_count = carrier_ids.carrier_id
        else:
            self._carrier_count = max(int(cid) for cid in carrier_ids)
        super().__init__(Knitout_Header_Line_Type.Carriers, self._carrier_count, comment)

    @property
    def carrier_count(self) -> int:
        """
        Returns:
            int: The number of carriers on this machine.
        """
        return self._carrier_count

    @property
    def carrier_str(self) -> str:
        """
        Returns:
            str: The string of carriers used to initialize the header string.
        """
        return " ".join(str(cid) for cid in range(1, self.carrier_count + 1))

    def value_matches_spec(self, specification: Knitting_Machine_Specification) -> bool:
        """
        Args:
            specification (Knitting_Machine_Specification): The machine specification to compare this header line to.

        Returns:
            bool: True if the given header value matches the value in the given specification.
        """
        carrier_count = self.header_type.get_specification_value(specification)
        return carrier_count == self._carrier_count

    def __str__(self) -> str:
        return f";;{self.header_type}: {self.carrier_str}{self.comment_str}"
