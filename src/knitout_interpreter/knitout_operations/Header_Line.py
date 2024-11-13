"""Module containing the classes for Header Lines in Knitout"""
from enum import Enum

from knit_graphs.Yarn import Yarn_Properties
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Type

from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


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

    def __str__(self):
        return f";;{self.header_type}: {self.header_value}{self.comment_str}"


class Machine_Header_Line(Knitout_Header_Line):

    def __init__(self, machine_type: str, comment: str | None = None):
        super().__init__(Knitout_Header_Line_Type.Machine, Knitting_Machine_Type[machine_type], comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.header_value != machine_state.machine_specification.machine:
            machine_state.machine_specification.machine = self.header_value
            return True
        else:
            return False


class Gauge_Header_Line(Knitout_Header_Line):

    def __init__(self, gauge: int, comment: str | None = None):
        super().__init__(Knitout_Header_Line_Type.Gauge, gauge, comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.header_value != machine_state.machine_specification.gauge:
            machine_state.machine_specification.gauge = self.header_value
            return True
        else:
            return False


class Position_Header_Line(Knitout_Header_Line):

    def __init__(self, position: str, comment: str | None = None):
        super().__init__(Knitout_Header_Line_Type.Position, position, comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if self.header_value != machine_state.machine_specification.position:
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

    def execute(self, machine_state: Knitting_Machine) -> bool:
        carrier_yarn_properties = machine_state.carrier_system[self.carrier_id].yarn.properties
        name_matched_properties = Yarn_Properties(carrier_yarn_properties.name, self.yarn_properties.plies, self.yarn_properties.weight, self.yarn_properties.color)
        # todo: override yarn-properties equality to ignore names in the knit-graphs package.
        if carrier_yarn_properties != name_matched_properties:
            machine_state.carrier_system[self.carrier_id].yarn = self.yarn_properties
            return True
        else:
            return False


class Carriers_Header_Line(Knitout_Header_Line):

    def __init__(self, carrier_ids: list[int], comment: str | None = None):
        super().__init__(Knitout_Header_Line_Type.Carriers, carrier_ids, comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        carrier_count = len(self.header_value)
        if len(machine_state.carrier_system.carriers) != carrier_count:
            machine_state.carrier_system = carrier_count
            return True
        return False
