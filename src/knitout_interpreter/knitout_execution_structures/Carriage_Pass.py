"""Modulce containing the Carriage Pass class."""
import time
import warnings

from knit_script.knitting_machine.machine_components.needles import Needle
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_warnings.carriage_pass_warnings import Reordered_Knitting_Pass_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction, Xfer_Instruction
from src.knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line, Knitout_Comment_Line


class Carriage_Pass:
    """Manages knitout operations that are organized in a single carriage pass."""
    def __init__(self, first_instruction: Needle_Instruction, rack: int, all_needle_rack: bool):
        self._creation_time = time.time()
        self.all_needle_rack: bool = all_needle_rack
        self.rack: int = rack
        self.xfer_pass: bool = isinstance(first_instruction, Xfer_Instruction)
        if self.xfer_pass:
            self.carrier_set: Yarn_Carrier_Set | None = None
            self._direction: Carriage_Pass_Direction | None = None
        else:
            self.carrier_set: Yarn_Carrier_Set | None = first_instruction.carrier_set
            self._direction: Carriage_Pass_Direction | None = first_instruction.direction
        self._instructions: list[Needle_Instruction] = [first_instruction]
        self._needles_to_instruction: dict[Needle, Needle_Instruction] = {first_instruction.needle: first_instruction}
        self._instruction_types_to_needles: dict[Knitout_Instruction_Type, dict[Needle, Needle_Instruction]] = {first_instruction.instruction_type:
                                                                                                                                 {first_instruction.needle: first_instruction}}

    def instruction_set(self) -> set[Needle_Instruction]:
        """
        :return: An unordered set of the instructions in the carriage pass.
        """
        return set(self._instructions)

    def rightward_sorted_needles(self) -> list[Needle]:
        """
        :return: List of needles in the carriage pass sorted from left to right.
        """
        return Carriage_Pass_Direction.Rightward.sort_needles(self._needles_to_instruction.keys(), self.rack)

    def leftward_sorted_needles(self) -> list[Needle]:
        """
        :return: List of needles in the carriage pass sorted from right to left.
        """
        return Carriage_Pass_Direction.Leftward.sort_needles(self._needles_to_instruction.keys(), self.rack)

    def sorted_needles(self) -> list[Needle]:
        """
        :return: List of needles in carriage pass sorted by direction of carriage pass or from left to right if no direction is given.
        """
        if self.direction is None:
            return self.rightward_sorted_needles()
        else:
            return self.direction.sort_needles(self._needles_to_instruction.keys(), self.rack)

    def instructions_by_needles(self, needles: list[Needle]) -> list[Needle_Instruction]:
        """
        :param needles: Ordered list of needles involved in the carriage pass.
        :return: The ordered set of instructions that start form the given needles.
        """
        return [self._needles_to_instruction[n] for n in needles]

    def carriage_pass_range(self) -> tuple[int, int]:
        """
        :return: Left most and Right most needle positions in the carriage pass.
        """
        sorted_needles = self.rightward_sorted_needles()
        return int(sorted_needles[0].racked_position_on_front(0)), int(sorted_needles[-1].racked_position_on_front(0))

    def rack_instruction(self, comment: str = "Racking for next carriage pass.") -> Rack_Instruction:
        """
        :return: Racking instruction to set up this carriage pass.
        """
        return Rack_Instruction.rack_instruction_from_int_specification(self.rack, self.all_needle_rack, comment)

    @property
    def direction(self) -> Carriage_Pass_Direction | None:
        """
        Setting the direction will reorder the instructions to the given direction. Should only be used to reorder Xfer Passes.
        :return: The direction of the carriage pass.
        """
        return self._direction

    @direction.setter
    def direction(self, direction: Carriage_Pass_Direction):
        if not self.xfer_pass:
            warnings.warn(Reordered_Knitting_Pass_Warning(direction, self))
        self._direction = direction
        sorted_needles = self.needles
        self._instructions = [self._needles_to_instruction[n] for n in sorted_needles]

    @property
    def needles(self) -> list[Needle]:
        """
        :return: Needles in order given by instruction set
        """
        needles = [i.needle for i in self._instructions]
        if self._direction is not None:
            return self._direction.sort_needles(needles, self.rack)
        else:
            return needles  # needles in order of given instructions

    @property
    def first_instruction(self) -> Needle_Instruction:
        """
        :return: First instruction given to carriage pass
        """
        return self._instructions[0]

    @property
    def last_instruction(self) -> Needle_Instruction:
        """
        :return: Last instruction executed in the given carriage pass.
        """
        return self._instructions[-1]

    @property
    def last_needle(self) -> Needle:
        """
        :return: Needle at the end of the ordered instructions
        """
        return self.needles[-1]

    def contains_instruction_type(self, instruction_type: Knitout_Instruction_Type) -> bool:
        """
        :param instruction_type: Instruction type to consider
        :return: True if the instruction type is used at least once in this carriage pass.
        """
        return instruction_type in self._instruction_types_to_needles

    def add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        """
        :param rack: The required racking of this instruction.
        :param all_needle_rack: The all_needle racking requirement for this instruction.
        :param instruction: The instruction to attempt to add to the carriage pass
        :return: True if instruction was added to pass.
            Otherwise, False implies that the instruction cannot be added to this carriage pass
        """
        # if instruction.direction is not self._direction or instruction.carrier_set != self.carrier_set:
        #     return False  # instruction is a change in direction or carrier set
        # if instruction.needle in self._needles_to_instruction:
        #     return False  # instruction requires a new pass because its needle is already in use.
        # if not self.compatible_with_pass_type(instruction):
        #     return False  # instruction is not of compatible type with this pass
        # if self._direction is not None and not self._direction.needles_are_in_pass_direction(self.last_needle, instruction.needle):
        #     return False  # instruction requires a new pass or change in direction
        if self.can_add_instruction(instruction, rack, all_needle_rack):
            self._instructions.append(instruction)
            self._needles_to_instruction[instruction.needle] = instruction
            if instruction.instruction_type not in self._instruction_types_to_needles:
                self._instruction_types_to_needles[instruction.instruction_type] = {}
            self._instruction_types_to_needles[instruction.instruction_type][instruction.needle] = instruction
            return True
        else:
            return False

    def compatible_with_pass_type(self, instruction: Needle_Instruction) -> bool:
        """
        :param instruction: The instruction to consider compatibility with.
        :return: True if instruction is compatible with this type of carriage pass.
        """
        return self.first_instruction.instruction_type.compatible_pass(instruction.instruction_type)

    def can_add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        """

        :param instruction: The instruction to consider adding to the carriage pass.
        :param rack: The required racking of this instruction.
        :param all_needle_rack: The all_needle racking requirement for this instruction.
        :return: True if the instruction can be added to this carriage pass. Otherwise, False.
        """
        if rack != self.rack:
            return False
        elif all_needle_rack != self.all_needle_rack:
            return False
        elif instruction.direction != self._direction:
            return False
        elif instruction.carrier_set != self.carrier_set:
            return False
        elif not self.compatible_with_pass_type(instruction):
            return False
        if self._direction is None:
            if instruction.needle in self._needles_to_instruction:
                return False
            elif instruction.needle_2 in self._needles_to_instruction:
                return False
        elif not self._direction.needles_are_in_pass_direction(self.last_needle, instruction.needle):
            return False
        return True

    def can_merge_pass(self, next_carriage_pass) -> bool:
        """
        :param next_carriage_pass: A carriage pass that happens immediately after this carriage pass.
        :return: Return True if these can be merged into one carriage pass.
        """
        if self.direction == next_carriage_pass.direction and self.compatible_with_pass_type(next_carriage_pass.first_instruction):
            next_left_needle, next_right_needle = next_carriage_pass.carriage_pass_range()
            if self.direction is Carriage_Pass_Direction.Rightward:
                return self.last_needle.position < next_left_needle
            elif self.direction is Carriage_Pass_Direction.Leftward:
                return self.last_needle.position > next_right_needle
        return False

    def merge_carriage_pass(self, next_carriage_pass, check_compatibility: bool = False) -> bool:
        """
        Merge the next carriage pass into this carriage pass.
        :param next_carriage_pass: A carriage pass that happens immediately after this carriage pass.
        :param check_compatibility: If true, checks compatibility before merging.
        :return: True if the merge was successful.
        """
        if check_compatibility and not self.can_merge_pass(next_carriage_pass):
            return False
        for instruction in next_carriage_pass:
            added = self.add_instruction(instruction, next_carriage_pass.rack_value, next_carriage_pass.all_needle_rack)
            assert added, f'Attempted to merge {self} and {next_carriage_pass} but failed to add {instruction}.'
        return True

    def execute(self, knitting_machine: Knitting_Machine) -> list[Knitout_Line]:
        """
        Executes carriage pass with an implied racking operation on the given knitting machine.
        Will default to ordering xfers in a rightward ascending direction.
        :param knitting_machine: The knitting machine to execute the carriage pass on.
        :return: A list of executed instructions from the carriage pass.
        """
        executed_instructions = []
        rack_instruction = self.rack_instruction()
        updated = rack_instruction.execute(knitting_machine)
        if updated:
            executed_instructions.append(rack_instruction)
        if self.xfer_pass:
            self.direction = Carriage_Pass_Direction.Rightward  # default xfers to be in ascending order
        for instruction in self:
            updated = instruction.execute(knitting_machine)
            if updated:
                executed_instructions.append(instruction)
            else:
                executed_instructions.append(Knitout_Comment_Line(instruction))
        return executed_instructions

    def __str__(self):
        string = ""
        indent = ""
        if not self.xfer_pass:
            string = f"in {self._direction} direction:"
            if len(self._instruction_types_to_needles) > 1:
                indent = "\t"
                string += "\n"
        for instruction_type, needles in self._instruction_types_to_needles.items():
            string += f"{indent}{instruction_type.value} {list(needles.keys())}"
        if self.xfer_pass:
            string += f" at {self.rack}"
        if self.carrier_set is not None:
            string += f" with {self.carrier_set}"
        string += "\n"
        return string

    def __list__(self) -> list[Knitout_Line]:
        return [*self]

    def __len__(self) -> int:
        return len(self._instructions)

    def __repr__(self):
        return str(self._instructions)

    def __iter__(self):
        return iter(self._instructions)

    def __getitem__(self, item: int | slice):
        return self._instructions[item]

    def __hash__(self):
        return hash(self._creation_time)
