"""Module containing the classes for Header Lines in Knitout"""
import warnings
from enum import Enum
from typing import Any

from knit_graphs.Yarn import Yarn_Properties
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Type, Knitting_Machine_Specification
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Knitting_Machine_Warning
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line, Knitout_Version_Line


class Knitout_Header_Line_Type(Enum):
    """Enumeration of properties that can be set in the header."""
    Machine = "Machine"
    Gauge = "Gauge"
    Yarn = "Yarn"
    Position = "Position"
    Carriers = "Carriers"

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


class Knitout_Header_Line(Knitout_Line):

    def __init__(self, header_type: Knitout_Header_Line_Type, header_value, comment: str | None):
        super().__init__(comment)
        self.header_value = header_value
        self.header_type: Knitout_Header_Line_Type = header_type

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """
        :param machine_state:
        :return: True if this header would update the given machine state. False, otherwise.
        """
        return False

    def __str__(self):
        return f";;{self.header_type}: {self.header_value}{self.comment_str}"


class Machine_Header_Line(Knitout_Header_Line):

    def __init__(self, machine_type: str, comment: str | None = None):
        super().__init__(Knitout_Header_Line_Type.Machine, Knitting_Machine_Type[machine_type], comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return self.header_value != machine_state.machine_specification.machine

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.machine_specification.machine = self.header_value
            return True
        else:
            return False


class Gauge_Header_Line(Knitout_Header_Line):

    def __init__(self, gauge: int, comment: str | None = None):
        super().__init__(Knitout_Header_Line_Type.Gauge, gauge, comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return self.header_value != machine_state.machine_specification.gauge

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.machine_specification.gauge = self.header_value
            return True
        else:
            return False


class Position_Header_Line(Knitout_Header_Line):

    def __init__(self, position: str, comment: str | None = None):
        super().__init__(Knitout_Header_Line_Type.Position, position, comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return self.header_value != machine_state.machine_specification.positio

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.machine_specification.position = self.header_value
            return True
        else:
            return False


class Yarn_Header_Line(Knitout_Header_Line):

    def __init__(self, carrier_id: int, plies: int, yarn_weight: float, color, comment: str | None = None):
        self.yarn_properties = Yarn_Properties(f"carrier+{carrier_id}_yarn", plies, yarn_weight, color)
        self.carrier_id = carrier_id
        super().__init__(Knitout_Header_Line_Type.Yarn, self.yarn_properties, comment)

    def __str__(self):
        return f";;{self.header_type}-{self.carrier_id}: {self.yarn_properties.plies}-{self.yarn_properties.weight} {self.yarn_properties.color}{self.comment_str}"

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return self.yarn_properties != machine_state.carrier_system[self.carrier_id].yarn.properties

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.updates_machine_state(machine_state):
            machine_state.carrier_system[self.carrier_id].yarn = self.yarn_properties
            return True
        else:
            return False


class Carriers_Header_Line(Knitout_Header_Line):

    def __init__(self, carrier_ids: list[int] | int | Yarn_Carrier_Set | Yarn_Carrier, comment: str | None = None):
        if isinstance(carrier_ids, int):
            carrier_ids = Yarn_Carrier_Set([i + 1 for i in range(carrier_ids)])
        elif isinstance(carrier_ids, Yarn_Carrier):
            carrier_ids = Yarn_Carrier_Set([carrier_ids.carrier_id])
        elif isinstance(carrier_ids, list):
            carrier_ids = Yarn_Carrier_Set(carrier_ids)
        super().__init__(Knitout_Header_Line_Type.Carriers, carrier_ids, comment)

    def updates_machine_state(self, machine_state: Knitting_Machine) -> bool:
        return len(machine_state.carrier_system.carriers) != len(self.header_value)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        carrier_count = len(self.header_value)
        if self.updates_machine_state(machine_state):
            machine_state.carrier_system = carrier_count
            return True
        return False


class Knitting_Machine_Header:
    """
        A class structure for maintain the relationship between header lines read from a knitout file and the state of a given knitting machine.
    """
    def __init__(self, knitting_machine: Knitting_Machine):
        self.machine: Knitting_Machine = knitting_machine
        self._header_lines: dict[Knitout_Header_Line_Type, Knitout_Header_Line] = {}

    def update_header(self, header_line: Knitout_Header_Line, update_machine: bool = False) -> bool:
        """

        :param header_line: The header line to update this header by.
        :param update_machine: If set to True, the header line will update the machine state to the new values in this header_line, if present.
            Otherwise, if set to False, the header line will only update this header if there is no explicitly set header line for that value.
            In this case, if the header line would require the machine state to update a warning is raised.
        :return: True if this header is updated by the given header line.
        """
        if header_line.header_type not in header_line:
            if update_machine:  # update the machine state and then add this to the header
                updated = header_line.execute(self.machine)
                if updated:
                    self._header_lines[header_line.header_type] = header_line
                    return True
                else:
                    return False
            else:
                would_update = header_line.updates_machine_state(self.machine)
                if would_update:
                    warnings.warn(Knitting_Machine_Warning(f"Ignored Header Updates Active Machine: {header_line}".rstrip()))
                elif header_line.header_type not in self._header_lines: # no change to machine state, but this line was never explicitly set.
                    self._header_lines[header_line.header_type] = header_line
                    return True
                return False

    def get_header_lines(self, version: int = 2) -> list[Knitout_Line]:
        """
        :param version: The number of the knitout version to process with.
        :return: List of header lines that form a complete knitout header from the given header. This starts with a given version line.
        """
        default_lines = {Knitout_Header_Line_Type.Machine: Machine_Header_Line(str(self.machine.machine_specification.machine)),
                         Knitout_Header_Line_Type.Gauge: Gauge_Header_Line(self.machine.machine_specification.gauge),
                         Knitout_Header_Line_Type.Position: Position_Header_Line(str(self.machine.machine_specification.position)),
                         Knitout_Header_Line_Type.Carriers: Carriers_Header_Line(self.machine.machine_specification.carrier_count)}
        for h_type, set_value in self._header_lines.items():
            default_lines[h_type] = set_value
        values = [Knitout_Version_Line(version)]
        values.extend(default_lines.values())
        return values


def get_machine_header(knitting_machine: Knitting_Machine, version: int = 2) -> list[Knitout_Line]:
    """
    :param knitting_machine: The machine state to specify as a header.
    :param version: The desired knitout version of the header.
    :return: A list of header and a version line that describes the given machine state.
    """
    header = Knitting_Machine_Header(knitting_machine)
    return header.get_header_lines(version)
