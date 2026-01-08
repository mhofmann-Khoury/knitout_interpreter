"""Module containing the Carriage Pass class."""

from __future__ import annotations

import time
import warnings
from collections.abc import Iterable, Iterator, Sequence
from typing import overload

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter._warning_stack_level_helper import get_user_warning_stack_level_from_knitout_interpreter_package
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line, Knitout_No_Op
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction, Xfer_Instruction
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction
from knitout_interpreter.knitout_warnings.Knitout_Warning import Reorder_Carriage_Pass_Warning


class Carriage_Pass:
    """Manages knitout operations that are organized in a single carriage pass.

    Attributes:
        all_needle_rack (bool): True if this carriage pass is set to allow all needle racking.
        rack (int): The offset racking alignment for the carriage pass.
    """

    def __init__(self, first_instruction: Needle_Instruction, rack: int, all_needle_rack: bool):
        """Initialize a new carriage pass with the first instruction.

        Args:
            first_instruction (Needle_Instruction): The first needle instruction in this carriage pass.
            rack (int): The rack position for this carriage pass.
            all_needle_rack (bool): Whether this pass uses all-needle racking.
        """
        self._creation_time: float = time.time()
        self.all_needle_rack: bool = all_needle_rack
        self.rack: int = rack
        self._xfer_pass: bool = isinstance(first_instruction, Xfer_Instruction)
        if self._xfer_pass:
            self._carrier_set: Yarn_Carrier_Set | None = None
            self._direction: Carriage_Pass_Direction | None = None
        else:
            self._carrier_set: Yarn_Carrier_Set | None = first_instruction.carrier_set
            self._direction: Carriage_Pass_Direction | None = first_instruction.direction
        self._instructions: list[Needle_Instruction] = [first_instruction]
        self._needles_to_instruction: dict[Needle, Needle_Instruction] = {first_instruction.needle: first_instruction}
        self._instruction_types_to_needles: dict[Knitout_Instruction_Type, dict[Needle, Needle_Instruction]] = {first_instruction.instruction_type: {first_instruction.needle: first_instruction}}

    @property
    def carrier_set(self) -> Yarn_Carrier_Set | None:
        """
        Returns:
            Yarn_Carrier_Set | None: The carrier set used in this carriage pass or None if the pass does not involve carriers.
        """
        return self._carrier_set

    @property
    def xfer_pass(self) -> bool:
        """
        Returns:
            bool: True if this carriage pass is transfer operations.
        """
        return self._xfer_pass

    def instruction_set(self) -> set[Needle_Instruction]:
        """
        Returns:
            set[Needle_Instruction]: An unordered set of the instructions in the carriage pass.
        """
        return set(self._instructions)

    def rightward_sorted_needles(self) -> list[Needle]:
        """
        Returns:
           list[Needle]: List of needles in the carriage pass sorted from left to right.
        """
        return Carriage_Pass_Direction.Rightward.sort_needles(self._needles_to_instruction.keys(), self.rack)

    def leftward_sorted_needles(self) -> list[Needle]:
        """
        Returns:
            list[Needle]: List of needles in the carriage pass sorted from right to left.
        """
        return Carriage_Pass_Direction.Leftward.sort_needles(self._needles_to_instruction.keys(), self.rack)

    def sorted_needles(self) -> list[Needle]:
        """
        Returns:
            list[Needle]:
                List of needles in carriage pass sorted by direction of carriage pass or from left to right if no direction is given.
        """
        if self.direction is None:
            return self.rightward_sorted_needles()
        else:
            return self.direction.sort_needles(self._needles_to_instruction.keys(), self.rack)

    def instruction_by_needle(self, needle: Needle) -> Needle_Instruction:
        """
        Args:
            needle (Needle): The needle to find the instruction of.

        Returns:
            Needle_Instruction: The instruction that operates on the given needle.

        Raise:
            KeyError: If the needle is not in the carriage pass.
        """
        return self._needles_to_instruction[needle]

    def instruction_by_slot(self, slot: int) -> Needle_Instruction | tuple[Needle_Instruction, Needle_Instruction]:
        """
        Args:
            slot (int): The needle slot to find an instruction on.

        Returns:
            Needle_Instruction | tuple[Needle_Instruction, Needle_Instruction]:
                The instruction that operates on the given slot.
                If both the front and back needle of the slot are used, returns a tuple of the front needle's instruction then the back needle's instruction.

        Raises:
            IndexError: If the slot is not in the carriage pass.
        """
        if not self.instruction_on_slot(slot):
            raise IndexError(f"No instruction on needle slot {slot} in {self}")
        front_needle = Needle(True, slot)
        front_instruction = self.instruction_by_needle(front_needle) if front_needle in self._needles_to_instruction else None
        back_needle = Needle(False, slot)
        back_instruction = self.instruction_by_needle(back_needle) if back_needle in self._needles_to_instruction else None
        if front_instruction is not None and back_instruction is not None:
            return front_instruction, back_instruction
        elif front_instruction is not None:
            return front_instruction
        elif back_instruction is not None:
            return back_instruction
        else:
            raise IndexError(f"No instruction on needle slot {slot} in {self}")

    def instructions_by_needles(self, needles: Sequence[Needle]) -> list[Needle_Instruction]:
        """
        Args:
            needles (Sequence[Needle]): Needles involved in the carriage pass.

        Returns:
            list[Needle_Instruction]: The ordered list of instructions that start from the given needles.
        """
        return [self._needles_to_instruction[n] for n in needles]

    def carriage_pass_range(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]:  The leftmost position and rightmost position in the carriage pass.
        """
        sorted_needles = self.rightward_sorted_needles()
        return int(sorted_needles[0].racked_position_on_front(rack=self.rack)), int(sorted_needles[-1].racked_position_on_front(rack=self.rack))

    def rack_instruction(self, comment: str = "Racking for next carriage pass.") -> Rack_Instruction:
        """
        Args:
            comment (str, optional): Comment to include with the racking instruction. Defaults to "Racking for next carriage pass."

        Returns:
            Rack_Instruction: Racking instruction to set up this carriage pass.
        """
        return Rack_Instruction.rack_instruction_from_int_specification(self.rack, self.all_needle_rack, comment)

    @property
    def direction(self) -> Carriage_Pass_Direction | None:
        """Get or set the direction of the carriage pass.

        Setting the direction will reorder the instructions to the given direction.
        Should only be used to reorder Xfer Passes.

        Returns:
            Carriage_Pass_Direction | None: The direction of the carriage pass.
        """
        return self._direction

    @direction.setter
    def direction(self, direction: Carriage_Pass_Direction) -> None:
        """Set the direction of the carriage pass.

        Args:
            direction (Carriage_Pass_Direction): The new direction for the carriage pass.

        Warns:
            Knitting_Machine_Warning: If the direction would change a directed carriage pass
        """
        if not self.xfer_pass and direction != self.direction:
            warnings.warn(
                Reorder_Carriage_Pass_Warning(self),
                stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package(),
            )
        self._direction = direction
        sorted_needles = self.needles
        self._instructions = [self._needles_to_instruction[n] for n in sorted_needles]

    @property
    def needles(self) -> list[Needle]:
        """
        Returns:
            list[Needle]: Needles in order given by instruction set.
        """
        needles = [i.needle for i in self._instructions]
        return self.direction.sort_needles(needles, self.rack) if self.direction is not None else needles

    @property
    def needle_slots(self) -> set[int]:
        """
        Returns:
            set[int]: The needle slot indices of needles used in this carriage pass.
        """
        return {n.position for n in self.needles}

    @property
    def first_instruction(self) -> Needle_Instruction:
        """Get the first instruction given to carriage pass.

        Returns:
            Needle_Instruction: First instruction given to carriage pass.
        """
        return self._instructions[0]

    @property
    def last_instruction(self) -> Needle_Instruction:
        """Get the last instruction executed in the carriage pass.

        Returns:
            Needle_Instruction: Last instruction executed in the given carriage pass.
        """
        return self._instructions[-1]

    @property
    def last_needle(self) -> Needle:
        """Get the needle at the end of the ordered instructions.

        Returns:
            Needle: Needle at the end of the ordered instructions.
        """
        return self.needles[-1]

    @property
    def first_needle(self) -> Needle:
        """
        Returns:
            Needle: The needle at the beginning of the ordered instructions.
        """
        return self.needles[0]

    @property
    def leftmost_slot(self) -> int:
        """
        Returns:
            int: The slot index of the leftmost needle in this carriage pass.
        """
        return min(self.first_needle.position, self.last_needle.position)

    @property
    def rightmost_slot(self) -> int:
        """
        Returns:
            int: The slot index of the rightmost needle in this carriage pass.
        """
        return max(self.first_needle.position, self.last_needle.position)

    def instruction_on_slot(self, slot: int | Needle) -> bool:
        """
        Args:
            slot (int | Needle): The slot index or a needle on that slot to check for.

        Returns:
            bool: True if the carriage pass has at least one instruction on the given slot, False otherwise.
        """
        return slot in self.needle_slots if isinstance(slot, int) else slot.position in self.needle_slots

    def contains_instruction_type(self, instruction_type: Knitout_Instruction_Type) -> bool:
        """Check if the carriage pass contains a specific instruction type.

        Args:
            instruction_type (Knitout_Instruction_Type): Instruction type to consider.

        Returns:
            bool: True if the instruction type is used at least once in this carriage pass. False, otherwise.
        """
        return instruction_type in self._instruction_types_to_needles

    def add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        """Attempt to add an instruction to the carriage pass.

        Args:
            instruction (Needle_Instruction): The instruction to attempt to add to the carriage pass.
            rack (int): The required racking of this instruction.
            all_needle_rack (bool): The all_needle racking requirement for this instruction.

        Returns:
            bool: True if instruction was added to pass. Otherwise, False implies that the instruction cannot be added to this carriage pass.
        """
        if self.can_add_instruction(instruction, rack, all_needle_rack):
            self._instructions.append(instruction)
            self._needles_to_instruction[instruction.needle] = instruction
            if instruction.instruction_type not in self._instruction_types_to_needles:
                self._instruction_types_to_needles[instruction.instruction_type] = {}
            self._instruction_types_to_needles[instruction.instruction_type][instruction.needle] = instruction
            return True
        else:
            return False

    def add_kicks(self, kicks: Iterable[Kick_Instruction]) -> None:
        """
        Adds the given kick instructions to the carriage pass. These kicks can be added at any slot that is not currently occupied by an instruction.

        Args:
            kicks (Iterable[Kick_Instruction]): The kicks to add to the carriage pass.

        Raises:
            ValueError: If adding kicks to a xfer pass without a specified direction or a kick uses a different carrier set than the one used by this carriage pass.
            IndexError: If adding a kick at a slot that is already occupied by an instruction.
        """
        if self.direction is None:
            raise ValueError("Cannot add kicks to transfer pass without specified direction.")
        if any(self.instruction_on_slot(k.position) for k in kicks):
            bad_slot = next(k.position for k in kicks if self.instruction_on_slot(k.position))
            raise IndexError(f"Cannot add kicks to needle slot {bad_slot} because an instruction {self[bad_slot]} is on that slot")
        if any(self.carrier_set != k.carrier_set for k in kicks):
            bad_cs = next(k for k in kicks if k.carrier_set != self.carrier_set)
            raise ValueError(f"Cannot add kicks with a different carrier set. Carrier set of {bad_cs} is not {self.carrier_set}")
        if Knitout_Instruction_Type.Kick not in self._instruction_types_to_needles:
            self._instruction_types_to_needles[Knitout_Instruction_Type.Kick] = {k.needle: k for k in kicks}
        all_instructions = list(self.instruction_set())
        all_instructions.extend(kicks)
        needles_to_instruction = {i.needle: i for i in all_instructions}
        sorted_needles = self.direction.sort_needles(needles_to_instruction, self.rack)
        sorted_instructions = [needles_to_instruction[n] for n in sorted_needles]
        self._instructions = sorted_instructions
        self._needles_to_instruction = {i.needle: i for i in self._instructions}

    def compatible_with_pass_type(self, instruction: Needle_Instruction) -> bool:
        """Check if an instruction is compatible with this type of carriage pass.

        Args:
            instruction (Needle_Instruction): The instruction to consider compatibility with.

        Returns:
            bool: True if instruction is compatible with this type of carriage pass.
        """
        return bool(self.first_instruction.instruction_type.compatible_pass(instruction.instruction_type))

    def can_add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        """Check if an instruction can be added to this carriage pass.

        Args:
            instruction (Needle_Instruction): The instruction to consider adding to the carriage pass.
            rack (int): The required racking of this instruction.
            all_needle_rack (all_needle_rack): The all_needle racking requirement for this instruction.

        Returns:
            bool: True if the instruction can be added to this carriage pass. Otherwise, False.
        """
        if (
            rack != self.rack
            or all_needle_rack != self.all_needle_rack
            or instruction.direction != self._direction
            or instruction.carrier_set != self.carrier_set
            or not self.compatible_with_pass_type(instruction)
            or instruction.needle in self._needles_to_instruction
        ):
            return False
        elif self._direction is None:
            if instruction.needle_2 in self._needles_to_instruction:
                return False
        elif (
            self.all_needle_rack  # All needle rack
            and instruction.needle.is_front != self.last_needle.is_front  # last and new instruction on opposite beds
            and instruction.needle.racked_position_on_front(self.rack) == self.last_needle.racked_position_on_front(self.rack)
        ):  # Last and new instruction at all-needle same position
            return True
        elif not self._direction.needles_are_in_pass_direction(self.last_needle, instruction.needle, self.rack, self.all_needle_rack):
            return False
        return True

    def can_merge_pass(self, next_carriage_pass: Carriage_Pass) -> bool:
        """Check if this carriage pass can be merged with the next one.

        Args:
            next_carriage_pass (Carriage_Pass): A carriage pass that happens immediately after this carriage pass.

        Returns:
            bool: True if these can be merged into one carriage pass. False, otherwise.
        """
        if self.direction == next_carriage_pass.direction and self.compatible_with_pass_type(next_carriage_pass.first_instruction):
            next_left_needle, next_right_needle = next_carriage_pass.carriage_pass_range()
            if self.direction is Carriage_Pass_Direction.Rightward:
                return bool(self.last_needle.position < next_left_needle)
            elif self.direction is Carriage_Pass_Direction.Leftward:
                return bool(self.last_needle.position > next_right_needle)
        return False

    def merge_carriage_pass(self, next_carriage_pass: Carriage_Pass, check_compatibility: bool = False) -> bool:
        """Merge the next carriage pass into this carriage pass.

        Args:
            next_carriage_pass (Carriage_Pass): A carriage pass that happens immediately after this carriage pass.
            check_compatibility (bool, optional): If true, checks compatibility before merging. Defaults to True

        Returns:
            bool: True if the merge was successful. False, otherwise.
        """
        if check_compatibility and not self.can_merge_pass(next_carriage_pass):
            return False
        for instruction in next_carriage_pass:
            added = self.add_instruction(instruction, next_carriage_pass.rack, next_carriage_pass.all_needle_rack)
            assert added, f"Attempted to merge {self} and {next_carriage_pass} but failed to add {instruction}."
        return True

    def execute(self, knitting_machine: Knitting_Machine) -> list[Needle_Instruction | Rack_Instruction | Knitout_Comment_Line]:
        """Execute carriage pass with an implied racking operation on the given knitting machine.

        Will default to ordering xfers in a rightward ascending direction.

        Args:
            knitting_machine (Knitting_Machine): The knitting machine to execute the carriage pass on.

        Returns:
            list[Needle_Instruction | Rack_Instruction | Knitout_Comment_Line]: A list of executed instructions from the carriage pass. Instructions that do not update the machine state are commented.
        """
        executed_instructions: list[Needle_Instruction | Rack_Instruction | Knitout_Comment_Line] = []
        rack_instruction = self.rack_instruction()
        updated = rack_instruction.execute(knitting_machine)
        if updated:
            executed_instructions.append(rack_instruction)
        if self._xfer_pass:
            self.direction = Carriage_Pass_Direction.Rightward  # default xfers to be in ascending order
        for instruction in self:
            updated = instruction.execute(knitting_machine)
            if updated:
                executed_instructions.append(instruction)
            else:
                executed_instructions.append(Knitout_No_Op(instruction))
        return executed_instructions

    def __str__(self) -> str:
        """Return string representation of the carriage pass.

        Returns:
            str: String representation showing direction, instruction types, and details.
        """
        string = ""
        indent = ""
        if not self._xfer_pass:
            string = f"in {self._direction} direction:"
            if len(self._instruction_types_to_needles) > 1:
                indent = "\t"
                string += "\n"
        for instruction_type, needles in self._instruction_types_to_needles.items():
            string += f"{indent}{instruction_type.value} {list(needles.keys())}"
        if self._xfer_pass:
            string += f" at {self.rack}"
        if self.carrier_set is not None:
            string += f" with {self.carrier_set}"
        string += "\n"
        return string

    def __list__(self) -> list[Needle_Instruction]:
        """Convert carriage pass to list of knitout lines.

        Returns:
            list[Needle_Instruction]: The list of needle instructions that form this carriage pass.
        """
        return [*self]

    def __len__(self) -> int:
        """Get the number of instructions in the carriage pass.

        Returns:
            int: Number of instructions in the carriage pass.
        """
        return len(self._instructions)

    def __repr__(self) -> str:
        """Return detailed representation of the carriage pass.

        Returns:
            str: String representation of the internal instructions list.
        """
        return str(self._instructions)

    def __iter__(self) -> Iterator[Needle_Instruction]:
        """Iterate over the instructions in the carriage pass.

        Returns:
            Iterator[Needle_Instruction]: Iterator over the instructions.
        """
        return iter(self._instructions)

    @overload
    def __getitem__(self, index: int) -> Needle_Instruction: ...

    @overload
    def __getitem__(self, index: slice) -> list[Needle_Instruction]: ...

    def __getitem__(self, item: int | slice) -> Needle_Instruction | list[Needle_Instruction]:
        """Get instruction(s) by index or slice.

        Args:
            item (int | slice): Index or slice to retrieve.

        Returns:
            Needle_Instruction | list[Needle_Instruction]: Instruction or list of instructions at the specified index/slice.
        """
        return self._instructions[item]

    def __hash__(self) -> int:
        """Get hash of the carriage pass based on creation time.

        Returns:
            int: Hash value based on creation time.
        """
        return hash(self._creation_time)


def carriage_pass_of_instructions(instructions: list[Needle_Instruction], rack: int = 0, all_needle_rack: bool = False) -> Carriage_Pass:
    """
    Args:
        instructions (list[Needle_Instruction]): List of instructions in the order that forms the carriage pass.
        rack (int, optional): Rack value of the carriage pass. Defaults to 0.
        all_needle_rack (bool, optional): If True, sets carriage pass to all needle racking. False by default.

    Returns:
        Carriage_Pass: The carriage pass formed by these instructions.
    """
    cp = Carriage_Pass(instructions[0], rack, all_needle_rack)
    if len(instructions) > 1:
        for instruction in instructions[1:]:
            cp.add_instruction(instruction, rack, all_needle_rack)
    return cp
