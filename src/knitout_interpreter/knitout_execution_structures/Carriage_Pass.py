"""Module containing the Carriage Pass class."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from typing import Any, ClassVar, Generic, TypeGuard, TypeVar, cast, overload

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Position, Needle_Specification

from knitout_interpreter.knitout_execution_structures.Knitout_Knitting_Machine import Knitout_Knitting_Machine
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line, Knitout_No_Op
from knitout_interpreter.knitout_operations.needle_instructions import (
    Drop_Instruction,
    Kick_Instruction,
    Knit_Pass_Instruction,
    Miss_Instruction,
    Needle_Instruction,
    Split_Instruction,
    Xfer_Instruction,
    Yarn_to_Needle_Instruction,
)
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction

Pass_Instruction_Type = TypeVar("Pass_Instruction_Type", bound=Knit_Pass_Instruction | Drop_Instruction | Miss_Instruction | Split_Instruction | Xfer_Instruction)


class Carriage_Pass(Generic[Pass_Instruction_Type]):
    """Manages knitout operations that are organized in a single carriage pass.

    Attributes:
        all_needle_rack (bool): True if this carriage pass is set to allow all needle racking.
        rack (int): The offset racking alignment for the carriage pass.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Carriage_Pass:
        """
        Counts the number of carriage passes created while running a program. Ensures a unique identifier for each carriage pass.
        """
        instance = super().__new__(cls)
        instance._creation_time = Carriage_Pass._next_cp()
        return instance

    def __init__(self, first_instruction: Pass_Instruction_Type, rack: int, all_needle_rack: bool):
        """Initialize a new carriage pass with the first instruction.

        Args:
            first_instruction (Yarn_to_Needle_Instruction | Xfer_Instruction): The first needle instruction in this carriage pass.
            rack (int): The rack position for this carriage pass.
            all_needle_rack (bool): Whether this pass uses all-needle racking.
        """
        self.all_needle_rack: bool = all_needle_rack
        self.rack: int = rack
        self._instructions: list[Pass_Instruction_Type] = [first_instruction]
        self._needles_to_instruction: dict[Needle_Specification, Pass_Instruction_Type] = {first_instruction.needle: first_instruction}
        self._instruction_types_to_needles: dict[type[Needle_Instruction], dict[Needle_Specification, Needle_Instruction]] = {type(first_instruction): {first_instruction.needle: first_instruction}}

    @property
    def first_instruction(self) -> Pass_Instruction_Type:
        """Get the first instruction given to carriage pass.

        Returns:
            Needle_Instruction: First instruction given to carriage pass.
        """
        return self._instructions[0]

    @property
    def xfer_pass(self) -> bool:
        """
        Returns:
            bool: True if this pass contains xfer instructions.
        """
        return isinstance(self.first_instruction, Xfer_Instruction)

    @property
    def directed_pass(self) -> bool:
        """
        Returns:
            bool: True if this pass is directed by a yarn-carrier movement.
        """
        return not self.xfer_pass

    @property
    def last_instruction(self) -> Pass_Instruction_Type:
        """Get the last instruction executed in the carriage pass.

        Returns:
            Needle_Instruction: Last instruction executed in the given carriage pass.
        """
        return self._instructions[-1]

    @property
    def needles(self) -> list[Needle_Specification]:
        """
        Returns:
            list[Needle_Specification]: Needles in order given by instruction set.
        """
        return [i.needle for i in self._instructions]

    @property
    def needle_slots(self) -> set[int]:
        """
        Returns:
            set[int]: The needle slot indices of needles used in this carriage pass.
        """
        return {n.slot_by_racking(self.rack) for n in self.needles}

    @property
    def last_needle(self) -> Needle_Specification:
        """Get the needle at the end of the ordered instructions.

        Returns:
            Needle_Specification: Needle at the end of the ordered instructions.
        """
        return self.needles[-1]

    @property
    def first_needle(self) -> Needle_Specification:
        """
        Returns:
            Needle_Specification: The needle at the beginning of the ordered instructions.
        """
        return self.needles[0]

    @property
    def leftmost_slot(self) -> int:
        """
        Returns:
            int: The slot index of the leftmost needle in this carriage pass.
        """
        return min(self.first_needle.slot_by_racking(self.rack), self.last_needle.slot_by_racking(self.rack))

    @property
    def rightmost_slot(self) -> int:
        """
        Returns:
            int: The slot index of the rightmost needle in this carriage pass.
        """
        return max(self.first_needle.slot_by_racking(self.rack), self.last_needle.slot_by_racking(self.rack))

    @property
    def carriage_pass_range(self) -> tuple[int, int]:
        """
        Returns:
            tuple[int, int]:  The leftmost position and rightmost position in the carriage pass.
        """
        return self.leftmost_slot, self.rightmost_slot

    @property
    def instruction_set(self) -> set[Pass_Instruction_Type]:
        """
        Returns:
            set[Pass_Instruction_Type]: An unordered set of the instructions in the carriage pass.
        """
        return set(self._instructions)

    @property
    def rightward_sorted_needles(self) -> list[Needle_Specification]:
        """
        Returns:
           list[Needle_Specification]: List of needles in the carriage pass sorted from left to right.
        """
        return Carriage_Pass_Direction.Rightward.sort_needles(self._needles_to_instruction.keys(), self.rack)

    @property
    def leftward_sorted_needles(self) -> list[Needle_Specification]:
        """
        Returns:
            list[Needle_Specification]: List of needles in the carriage pass sorted from right to left.
        """
        return Carriage_Pass_Direction.Leftward.sort_needles(self._needles_to_instruction.keys(), self.rack)

    @property
    def sorted_needles(self) -> list[Needle_Specification]:
        """
        Returns:
            list[Needle_Specification]: List of needles in carriage pass sorted by direction of carriage pass or from left to right if instructions are undirected.
        """
        if isinstance(self.first_instruction, Yarn_to_Needle_Instruction):
            return self.first_instruction.direction.sort_needles(self.needles, self.rack)
        else:
            return self.rightward_sorted_needles

    def instruction_by_needle(self, needle: Needle_Specification) -> Pass_Instruction_Type:
        """
        Args:
            needle (Needle_Specification): The needle to find the instruction of.

        Returns:
            Pass_Instruction_Type: The instruction that operates on the given needle.

        Raise:
            KeyError: If the needle is not in the carriage pass.
        """
        return self._needles_to_instruction[needle]

    def instruction_on_slot(self, slot: int | Needle_Specification) -> bool:
        """
        Args:
            slot (int | Needle_Specification): The slot index or a needle on that slot to check for.

        Returns:
            bool: True if the carriage pass has at least one instruction on the given slot, False otherwise.
        """
        return slot in self.needle_slots if isinstance(slot, int) else slot.slot_by_racking(self.rack) in self.needle_slots

    def instruction_by_slot(self, slot: int) -> Pass_Instruction_Type | tuple[Pass_Instruction_Type, Pass_Instruction_Type]:
        """
        Args:
            slot (int): The needle slot to find an instruction on.

        Returns:
            Pass_Instruction_Type | tuple[Pass_Instruction_Type, Pass_Instruction_Type]:
                The instruction that operates on the given slot.
                If both the front and back needle of the slot are used, returns a tuple of the front needle's instruction then the back needle's instruction.

        Raises:
            IndexError: If the slot is not in the carriage pass.
        """
        if not self.instruction_on_slot(slot):
            raise IndexError(f"No instruction on needle slot {slot} in {self}")
        front_needle = Needle_Position(True, slot, is_slider=False)
        front_instruction = self.instruction_by_needle(front_needle) if front_needle in self._needles_to_instruction else None
        back_needle = Needle_Position(False, slot, is_slider=False)
        back_instruction = self.instruction_by_needle(back_needle) if back_needle in self._needles_to_instruction else None
        if front_instruction is not None and back_instruction is not None:
            return front_instruction, back_instruction
        elif front_instruction is not None:
            return front_instruction
        elif back_instruction is not None:
            return back_instruction
        else:
            raise IndexError(f"No instruction on needle slot {slot} in {self}")

    def instructions_by_needles(self, needles: Sequence[Needle_Specification]) -> list[Pass_Instruction_Type]:
        """
        Args:
            needles (Sequence[Needle_Specification]): Needles involved in the carriage pass.

        Returns:
            list[Pass_Instruction_Type]: The ordered list of instructions that start from the given needles.
        """
        return [self.instruction_by_needle(n) for n in needles]

    def rack_instruction(self, comment: str = "Racking for next carriage pass.") -> Rack_Instruction:
        """
        Args:
            comment (str, optional): Comment to include with the racking instruction. Defaults to "Racking for next carriage pass."

        Returns:
            Rack_Instruction: Racking instruction to set up this carriage pass.
        """
        return Rack_Instruction.rack_instruction_from_int_specification(self.rack, self.all_needle_rack, comment)

    def contains_instruction_type(self, instruction_type: type[Needle_Instruction]) -> bool:
        """Check if the carriage pass contains a specific instruction type.

        Args:
            instruction_type (type(Needle_Instruction)): Instruction type to consider.

        Returns:
            bool: True if the instruction type is used at least once in this carriage pass. False, otherwise.
        """
        return instruction_type in self._instruction_types_to_needles

    def can_add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        """Check if an instruction can be added to this carriage pass.

        Args:
            instruction (Needle_Instruction): The instruction to consider adding to the carriage pass.
            rack (int): The required racking of this instruction.
            all_needle_rack (all_needle_rack): The all_needle racking requirement for this instruction.

        Returns:
            bool: True if the instruction can be added to this carriage pass. Otherwise, False.

        Notes:
            Requirements to add to Pass:
            * Instruction must be at the same racking as this carriage pass
            * The instruction's needle cannot already be used in this pass.
            * The instruction must be of a compatible type with the instructions in this pass.
            * If the instruction is directed and uses a yarn carrier, these values must match.
                * If the pass is all-needle knit and the values may be on the same slot (i.e, front and back bed).
                * The slot of this instruction must come after the slot of the last instruction.
        """
        if rack != self.rack or all_needle_rack != self.all_needle_rack or instruction.needle in self._needles_to_instruction or not self.first_instruction.compatible_in_carriage_pass(instruction):
            return False
        elif isinstance(self.first_instruction, Yarn_to_Needle_Instruction) and isinstance(instruction, Yarn_to_Needle_Instruction):
            if self.first_instruction.direction != instruction.direction or self.first_instruction.carrier_set != instruction.carrier_set:
                return False
            if (
                self.all_needle_rack
                and instruction.needle.is_front != self.last_needle.is_front  # last and new instruction on opposite beds
                and instruction.needle.slot_by_racking(self.rack) == self.last_needle.slot_by_racking(self.rack)
            ):  # Last and new instruction at all-needle same position
                return True
            elif self.first_instruction.direction is Carriage_Pass_Direction.Leftward:
                return self.last_needle.slot_by_racking(self.rack) > instruction.needle.slot_by_racking(self.rack)
            else:  # Rightward direction
                return self.last_needle.slot_by_racking(self.rack) < instruction.needle.slot_by_racking(self.rack)
        else:
            return True

    def add_instruction(self, instruction: Pass_Instruction_Type, rack: int, all_needle_rack: bool) -> bool:
        """Attempt to add an instruction to the carriage pass.

        Args:
            instruction (Pass_Instruction_Type): The instruction to attempt to add to the carriage pass.
            rack (int): The required racking of this instruction.
            all_needle_rack (bool): The all_needle racking requirement for this instruction.

        Returns:
            bool: True if instruction was added to pass. Otherwise, False implies that the instruction cannot be added to this carriage pass.
        """
        if self.can_add_instruction(instruction, rack, all_needle_rack):
            self._instructions.append(instruction)
            self._needles_to_instruction[instruction.needle] = instruction
            if type(instruction) not in self._instruction_types_to_needles:
                self._instruction_types_to_needles[type(instruction)] = {}
            self._instruction_types_to_needles[type(instruction)][instruction.needle] = instruction
            return True
        else:
            return False

    def can_merge_pass(self, next_carriage_pass: Carriage_Pass) -> bool:
        """
        Args:
            next_carriage_pass (Carriage_Pass): A carriage pass that happens immediately after this carriage pass.

        Returns:
            bool: True if these can be merged into one carriage pass. False, otherwise.
        """
        return self.can_add_instruction(next_carriage_pass.first_instruction, next_carriage_pass.rack, next_carriage_pass.all_needle_rack)

    def merge_carriage_pass(self, next_carriage_pass: Carriage_Pass) -> TypeGuard[Carriage_Pass[Pass_Instruction_Type]]:
        """Merge the next carriage pass into this carriage pass.

        Args:
            next_carriage_pass (Carriage_Pass): A carriage pass that happens immediately after this carriage pass.

        Returns:
            bool, TypeGuard[Carriage_Pass[Pass_Instruction_Type]]:
                True if the merge was successful. False, otherwise.
                TypeGuard guarantees that the merged pass has the same Pass_Instruction_Type as this pass.
        """
        if not self.can_merge_pass(next_carriage_pass):
            return False
        for instruction in next_carriage_pass:
            added = self.add_instruction(instruction, next_carriage_pass.rack, next_carriage_pass.all_needle_rack)
            assert added, f"Attempted to merge {self} and {next_carriage_pass} but failed to add {instruction}."
        return True

    def add_kicks(self, kicks: Iterable[Kick_Instruction]) -> None:
        """
        Adds the given kick instructions to the carriage pass. These kicks can be added at any slot that is not currently occupied by an instruction.

        Args:
            kicks (Iterable[Kick_Instruction]): The kicks to add to the carriage pass.

        Raises:
            ValueError: If adding kicks to a xfer pass without a specified direction or a kick uses a different carrier set than the one used by this carriage pass.
            IndexError: If adding a kick at a slot that is already occupied by an instruction.
        """
        if not isinstance(self.first_instruction, Knit_Pass_Instruction):
            raise ValueError(f"Cannot add carrier-kickbacks to pass with instructions of type {type(self.first_instruction)}")
        if any(self.instruction_on_slot(k.position) for k in kicks):
            bad_slot = next(k.position for k in kicks if self.instruction_on_slot(k.position))
            raise IndexError(f"Cannot add kicks to needle slot {bad_slot} because an instruction {self[bad_slot]} is on that slot")
        if any(self.first_instruction.carrier_set != k.carrier_set for k in kicks):
            bad_cs = next(k for k in kicks if k.carrier_set != self.first_instruction.carrier_set)
            raise ValueError(f"Cannot add kicks with a different carrier set. Carrier set of {bad_cs} is not {self.first_instruction.carrier_set}")
        if Kick_Instruction not in self._instruction_types_to_needles:
            self._instruction_types_to_needles[Kick_Instruction] = {k.needle: k for k in kicks}
        all_instructions = [*self, *kicks]
        needles_to_instruction = {i.needle: i for i in all_instructions}
        sorted_needles = self.first_instruction.direction.sort_needles(needles_to_instruction, self.rack)
        sorted_instructions = [needles_to_instruction[n] for n in sorted_needles]
        self._instructions: list[Pass_Instruction_Type] = cast(list[Pass_Instruction_Type], sorted_instructions)
        self._needles_to_instruction: dict[Needle_Specification, Pass_Instruction_Type] = {i.needle: i for i in self._instructions}

    def execute(self, knitting_machine: Knitout_Knitting_Machine) -> list[Pass_Instruction_Type | Rack_Instruction | Knitout_Comment_Line]:
        """Execute carriage pass with an implied racking operation on the given knitting machine.

        Will default to ordering xfers in a rightward ascending direction.

        Args:
            knitting_machine (Knitting_Machine): The knitting machine to execute the carriage pass on.

        Returns:
            list[Pass_Instruction_Type | Rack_Instruction | Knitout_Comment_Line]:
                A list of executed instructions from the carriage pass.
                Instructions that do not update the machine state are commented.
        """
        executed_instructions: list[Pass_Instruction_Type | Rack_Instruction | Knitout_Comment_Line] = []
        rack_instruction = self.rack_instruction()
        updated = rack_instruction.execute(knitting_machine)
        if updated:
            executed_instructions.append(rack_instruction)
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
        if isinstance(self.first_instruction, Yarn_to_Needle_Instruction):
            string = f"with {self.first_instruction.carrier_set} in {self.first_instruction.direction} direction:"
            if len(self._instruction_types_to_needles) > 1:
                indent = "\t"
                string += "\n"

        for instruction_type, needles in self._instruction_types_to_needles.items():
            string += f"{indent}{instruction_type.instruction_type.value} {list(needles.keys())}"
        if self.rack != 0:
            string += f" at {self.rack}"
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

    def __iter__(self) -> Iterator[Pass_Instruction_Type]:
        """Iterate over the instructions in the carriage pass.

        Returns:
            Iterator[Pass_Instruction_Type]: Iterator over the instructions.
        """
        return iter(self._instructions)

    @overload
    def __getitem__(self, index: int) -> Pass_Instruction_Type: ...

    @overload
    def __getitem__(self, index: slice) -> list[Pass_Instruction_Type]: ...

    def __getitem__(self, item: int | slice) -> Pass_Instruction_Type | list[Pass_Instruction_Type]:
        """Get instruction(s) by index or slice.

        Args:
            item (int | slice): Index or slice to retrieve.

        Returns:
            Pass_Instruction_Type | list[Pass_Instruction_Type]: Instruction or list of instructions at the specified index/slice.
        """
        return self._instructions[item]

    def __hash__(self) -> int:
        """
        Returns:
            int: Hash value based on creation time.
        """
        return hash(self._creation_time)

    _cp_made: ClassVar[int] = 0

    @staticmethod
    def _next_cp() -> int:
        """
        Tick up the count of knitout_lines instantiated.
        Returns:
            int: The current line count before the number ticked up.
        """
        cur = Carriage_Pass._cp_made
        Carriage_Pass._cp_made += 1
        return cur


@overload
def carriage_pass_typed_to_first_instruction(
    first_instruction: Xfer_Instruction,
    rack: int,
    all_needle_rack: bool,
) -> Carriage_Pass[Xfer_Instruction]: ...


@overload
def carriage_pass_typed_to_first_instruction(
    first_instruction: Split_Instruction,
    rack: int,
    all_needle_rack: bool,
) -> Carriage_Pass[Split_Instruction]: ...


@overload
def carriage_pass_typed_to_first_instruction(
    first_instruction: Drop_Instruction,
    rack: int,
    all_needle_rack: bool,
) -> Carriage_Pass[Drop_Instruction]: ...


@overload
def carriage_pass_typed_to_first_instruction(
    first_instruction: Knit_Pass_Instruction,
    rack: int,
    all_needle_rack: bool,
) -> Carriage_Pass[Knit_Pass_Instruction]: ...


@overload
def carriage_pass_typed_to_first_instruction(
    first_instruction: Miss_Instruction,
    rack: int,
    all_needle_rack: bool,
) -> Carriage_Pass[Miss_Instruction]: ...


def carriage_pass_typed_to_first_instruction(
    first_instruction: Xfer_Instruction | Split_Instruction | Drop_Instruction | Knit_Pass_Instruction | Miss_Instruction,
    rack: int,
    all_needle_rack: bool,
) -> Carriage_Pass[Xfer_Instruction] | Carriage_Pass[Split_Instruction] | Carriage_Pass[Drop_Instruction] | Carriage_Pass[Knit_Pass_Instruction] | Carriage_Pass[Miss_Instruction]:
    """
    Args:
        first_instruction (Needle_Instruction): First instruction to carriage pass.
        rack (int): The racking of the carriage pass.
        all_needle_rack (bool): True if the carriage pass operates at an all needle rack.

    Returns:
        Carriage_Pass[Pass_Instruction_Type]: The carriage pass typed to the type of the first instruction.
    """
    if isinstance(first_instruction, Xfer_Instruction):
        return Carriage_Pass[Xfer_Instruction](first_instruction, rack, all_needle_rack)
    elif isinstance(first_instruction, Split_Instruction):
        return Carriage_Pass[Split_Instruction](first_instruction, rack, all_needle_rack)
    elif isinstance(first_instruction, Drop_Instruction):
        return Carriage_Pass[Drop_Instruction](first_instruction, rack, all_needle_rack)
    elif isinstance(first_instruction, Knit_Pass_Instruction):
        return Carriage_Pass[Knit_Pass_Instruction](first_instruction, rack, all_needle_rack)
    elif isinstance(first_instruction, Miss_Instruction):
        return Carriage_Pass[Miss_Instruction](first_instruction, rack, all_needle_rack)
    else:
        raise TypeError(f"Instruction {first_instruction} is not recognized as a type of carriage pass.")


def carriage_pass_of_instructions(instructions: list[Pass_Instruction_Type], rack: int = 0, all_needle_rack: bool = False) -> Carriage_Pass[Pass_Instruction_Type]:
    """
    Args:
        instructions (list[Pass_Instruction_Type]): List of instructions in the order that forms the carriage pass.
        rack (int, optional): Rack value of the carriage pass. Defaults to 0.
        all_needle_rack (bool, optional): If True, sets carriage pass to all needle racking. False by default.

    Returns:
        Carriage_Pass: The carriage pass formed by these instructions.
    """
    cp = Carriage_Pass[Pass_Instruction_Type](instructions[0], rack, all_needle_rack)
    if len(instructions) > 1:
        for instruction in instructions[1:]:
            cp.add_instruction(instruction, rack, all_needle_rack)
    return cp
