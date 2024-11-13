"""Needle operations"""
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_exceptions.Needle_Exception import Misaligned_Needle_Exception
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn

from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction, Knitout_Instruction_Type


class Needle_Instruction(Knitout_Instruction):

    def __init__(self, instruction_type: Knitout_Instruction_Type,
                 needle: Needle, direction: None | str | Carriage_Pass_Direction = None, needle_2: None | Needle = None,
                 carrier_set: None | Yarn_Carrier_Set = None,
                 comment: None | str = None):
        super().__init__(instruction_type, comment)
        self.carrier_set = carrier_set
        self.needle_2 = needle_2
        if direction is not None and isinstance(direction, str):
            direction = Carriage_Pass_Direction.get_direction(direction)
        self.direction: None | Carriage_Pass_Direction = direction
        self.needle = needle
        self.carriage_pass = None
        self.made_loops: list[Machine_Knit_Loop] = []
        self.moved_loops: list[Machine_Knit_Loop] = []
        self.dropped_loops: list[Machine_Knit_Loop] = []

    def get_yarns(self, knitting_machine: Knitting_Machine) -> dict[int, Machine_Knit_Yarn]:
        """

        :param knitting_machine: The knitting machine to access yarn data from.
        :return: Dictionary of carrier ids to the yarn that is currently active on them.
        """
        return {cid: carrier.yarn for cid, carrier in self.get_carriers(knitting_machine).items()}

    def get_carriers(self, knitting_machine: Knitting_Machine) -> dict[int, Yarn_Carrier]:
        """
        :param knitting_machine: The knitting machine to access carrier data from.
        :return: Dictionary of carrier ids keyed to the carrier that is currently active on them.
        """
        if self.carrier_set is None:
            return {}
        else:
            return {cid: knitting_machine.carrier_system[cid] for cid in self.carrier_set.carrier_ids}

    @property
    def has_second_needle(self) -> bool:
        """
        :return: True if it has a second needle
        """
        return self.needle_2 is not None

    @property
    def has_direction(self) -> bool:
        """
        :return: True if it has a direction value
        """
        return self.direction is not None

    @property
    def has_carrier_set(self) -> bool:
        """
        :return: true if it has carrier set
        """
        return self.carrier_set is not None

    @property
    def implied_racking(self) -> None | int:
        """
        :return: None if no specific racking is required or the required racking value to complete this operation.
        """
        if not self.has_second_needle:
            return None
        else:
            if self.needle.is_front:
                return Knitting_Machine.get_transfer_rack(self.needle, self.needle_2)

    def _test_operation(self):
        if self.instruction_type.directed_pass:
            assert self.has_direction, f"Cannot {self.instruction_type} without a direction"
        if self.instruction_type.requires_second_needle:
            assert self.has_second_needle, f"Cannot {self.instruction_type} without target needle"
        if self.instruction_type.requires_carrier:
            assert self.has_carrier_set, f"Cannot {self.instruction_type} without a carrier set"

    def __str__(self):
        if self.has_direction:
            dir_str = f" {self.direction}"
        else:
            dir_str = ""
        if self.has_second_needle:
            n2_str = f" {self.needle_2}"
        else:
            n2_str = ""
        if self.has_carrier_set:
            cs_str = f" {self.carrier_set}"
        else:
            cs_str = ""
        return f"{self.instruction_type}{dir_str} {self.needle}{n2_str}{cs_str}{self.comment_str}"


class Loop_Making_Instruction(Needle_Instruction):

    def __init__(self, instruction_type: Knitout_Instruction_Type,
                 needle: Needle, direction: None | str | Carriage_Pass_Direction = None,
                 needle_2: None | Needle = None,
                 carrier_set: Yarn_Carrier_Set = None,
                 comment: None | str = None):
        super().__init__(instruction_type, needle, direction, needle_2, carrier_set, comment)


class Knit_Instruction(Loop_Making_Instruction):

    def __init__(self, needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Knit, needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitting_Machine):
        self._test_operation()
        self.dropped_loops, self.made_loops = machine_state.knit(self.carrier_set, self.needle, self.direction)
        return True  # true even if loops is empty because the prior loops are dropped.

    @staticmethod
    def execute_knit(machine_state: Knitting_Machine,
                     needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set,
                     comment: str | None = None):
        """
            :param needle: The needle to execute on.
            :param direction: The direction to execute in.
            :param cs: The yarn carriers set to execute with.
            :param machine_state: The current machine model to update.
            :param comment: Additional details to document in the knitout.
            :return: The instruction.
            """
        instruction = Knit_Instruction(needle, direction, cs, comment)
        instruction.execute(machine_state)
        return instruction


class Tuck_Instruction(Loop_Making_Instruction):

    def __init__(self, needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Tuck, needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitting_Machine):
        self._test_operation()
        self.made_loops = machine_state.tuck(self.carrier_set, self.needle, self.direction)
        return len(self.made_loops) > 0

    @staticmethod
    def execute_tuck(machine_state: Knitting_Machine,
                     needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set,
                     comment: str | None = None):
        """
            :param needle: The needle to execute on.
            :param direction: The direction to execute in.
            :param cs: The yarn carriers set to execute with.
            :param machine_state: The current machine model to update.
            :param comment: Additional details to document in the knitout.
            :return: The instruction.
            """
        instruction = Tuck_Instruction(needle, direction, cs, comment)
        instruction.execute(machine_state)
        return instruction


class Split_Instruction(Loop_Making_Instruction):

    def __init__(self, needle: Needle, direction: Carriage_Pass_Direction, n2: Needle, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Split, needle, direction=direction, needle_2=n2, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitting_Machine):
        self._test_operation()
        aligned_needle = machine_state.get_aligned_needle(self.needle)
        if aligned_needle != self.needle_2:
            raise Misaligned_Needle_Exception(self.needle, self.needle_2)
        self.made_loops, self.moved_loops = machine_state.split(self.carrier_set, self.needle, self.direction)
        return len(self.made_loops) > 0 or len(self.moved_loops) > 0

    @staticmethod
    def execute_split(machine_state: Knitting_Machine,
                      needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, n2: Needle,
                      comment: str | None = None):
        """
            :param n2: The second needle to execute to.
            :param needle: The needle to execute on.
            :param direction: The direction to execute in.
            :param cs: The yarn carriers set to execute with.
            :param machine_state: The current machine model to update.
            :param comment: Additional details to document in the knitout.
            :return: The instruction.
            """
        instruction = Split_Instruction(needle, direction, n2, cs, comment)
        instruction.execute(machine_state)
        return instruction


class Drop_Instruction(Needle_Instruction):

    def __init__(self, needle: Needle, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Drop, needle, comment=comment)

    def execute(self, machine_state: Knitting_Machine):
        self._test_operation()
        self.dropped_loops = machine_state.drop(self.needle)
        return True

    @staticmethod
    def execute_Drop(machine_state: Knitting_Machine,
                     needle: Needle, comment: str | None = None):
        """
            :param needle: The needle to execute on.
            :param machine_state: The current machine model to update.
            :param comment: Additional details to document in the knitout.
            :return: The instruction.
            """
        instruction = Drop_Instruction(needle, comment)
        instruction.execute(machine_state)
        return instruction


class Xfer_Instruction(Needle_Instruction):

    def __init__(self, needle: Needle, n2: Needle, comment: None | str = None, record_location=True):
        super().__init__(Knitout_Instruction_Type.Xfer, needle, needle_2=n2, comment=comment)
        self.record_location = record_location
        self.loop_crossings_made: dict[Machine_Knit_Loop, list[Machine_Knit_Loop]] = {}  # Todo: Use loop crossing code.

    def add_loop_crossing(self, left_loop: Machine_Knit_Loop, right_loop: Machine_Knit_Loop):
        """
        Update loop crossing to show transfers crossing loops.
        :param left_loop: The left loop involved in the crossing.
        :param right_loop: The Right loop involved in the crossing.
        """
        if left_loop not in self.loop_crossings_made:
            self.loop_crossings_made[left_loop] = []
        self.loop_crossings_made[left_loop].append(right_loop)

    def execute(self, machine_state: Knitting_Machine):
        self._test_operation()
        to_slider = self.needle_2.is_slider
        aligned_needle = machine_state.get_aligned_needle(self.needle, aligned_slider=to_slider)
        if aligned_needle != self.needle_2:
            raise Misaligned_Needle_Exception(self.needle, self.needle_2)
        self.moved_loops = machine_state.xfer(self.needle, to_slider=to_slider)
        return len(self.moved_loops) > 0

    @staticmethod
    def execute_xfer(machine_state: Knitting_Machine,
                     needle: Needle, n2: Needle,
                     comment: str | None = None):
        """
            :param n2: The second needle to execute to.
            :param needle: The needle to execute on.
            :param machine_state: The current machine model to update.
            :param comment: Additional details to document in the knitout.
            :return: The instruction.
            """
        instruction = Xfer_Instruction(needle, n2, comment)
        instruction.execute(machine_state)
        return instruction


class Miss_Instruction(Needle_Instruction):

    def __init__(self, needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Miss, needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state):
        """
        Positions the carrier above the give needle.
        :param machine_state: The machine state to update.
        """
        self._test_operation()
        machine_state.miss(self.carrier_set, self.needle, self.direction)
        return True

    @staticmethod
    def execute_miss(machine_state: Knitting_Machine,
                     needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set,
                     comment: str | None = None):
        """
            :param needle: The needle to execute on.
            :param direction: The direction to execute in.
            :param cs: The yarn carriers set to execute with.
            :param machine_state: The current machine model to update.
            :param comment: Additional details to document in the knitout.
            :return: The instruction.
            """
        instruction = Miss_Instruction(needle, direction, cs, comment)
        instruction.execute(machine_state)
        return instruction
