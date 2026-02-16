"""Needle operations"""

from __future__ import annotations

from typing import Any, ClassVar, TypeVar

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Position, Needle_Specification
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_execution_structures.Knitout_Knitting_Machine import Knitout_Knitting_Machine
from knitout_interpreter.knitout_execution_structures.knitout_loops import Knitout_Loop
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction, Knitout_Instruction_Type

Knitout_LoopT = TypeVar("Knitout_LoopT", bound=Knitout_Loop)


class Needle_Instruction(Knitout_Instruction):
    """
    The base class for all instructions that execute on a needle.

    Attributes:
        _made_loops (list[Knitout_Loop]): The list of loops that were made by this instruction.
        _moved_loops (list[Knitout_Loop]): The list of loops that transferred by this instruction.
        _dropped_loops (list[Knitout_Loop]): The list of loops that dropped by this instruction.
    """

    _deepcopy_defaults: ClassVar[dict[str, Any]] = {
        "_moved_loops": [],
        "_made_loops": [],
        "_dropped_loops": [],
    }

    def __init__(self, needle: Needle_Specification, comment: str | None = None, **_kwargs: Any):
        super().__init__(comment, interrupts_carriage_pass=False)
        self._needle: Needle_Specification = needle
        self._dropped_loops: list[Knitout_Loop] = []
        self._moved_loops: list[Knitout_Loop] = []
        self._made_loops: list[Knitout_Loop] = []

    @property
    def needle(self) -> Needle_Specification:
        """
        Returns:
            Needle_Specification: The needle that this operation executes on.
        """
        return self._needle

    @property
    def effected_loops(self) -> bool:
        """
        Returns:
            bool: True if this instruction effected loops by creating them, dropping them, or moving them in the last execution.
        """
        return len(self._made_loops) > 0 or len(self._moved_loops) > 0 or len(self._dropped_loops) > 0

    def compatible_in_carriage_pass(self, other_instruction: Needle_Instruction) -> bool:
        """
        By default, instructions are compatible if they are of the same subclass type (i.e., xfers can only share a pass with xfers, splits with splits, drops with drops).

        Args:
            other_instruction (Needle_Instruction): The other instruction to test.

        Returns:
            bool: True if the other instruction can be performed in the same carriage pass as this instruction.
        """
        return isinstance(other_instruction, self.__class__)

    @property
    def _dir_str(self) -> str:
        return ""

    @property
    def _n2_str(self) -> str:
        return ""

    @property
    def _carrier_str(self) -> str:
        return ""

    def __str__(self) -> str:
        return f"{self.instruction_type}{self._dir_str} {self.needle}{self._n2_str}{self._carrier_str}{self.comment_str}"


class Dropping_Instruction(Needle_Instruction):
    _deepcopy_defaults: ClassVar[dict[str, Any]] = {
        "_dropped_loops": [],
    }

    def __init__(self, needle: Needle_Specification, comment: str | None = None, **_kwargs: Any):
        super().__init__(needle=needle, comment=comment, **_kwargs)
        self._dropped_loops: list[Knitout_Loop] = []

    @property
    def dropped_loops(self) -> list[Knitout_Loop]:
        """
        Returns:
            list[Knitout_Loop]: The list of loops dropped from the needle bed by this instruction during its last execution.
        """
        return self._dropped_loops

    @dropped_loops.setter
    def dropped_loops(self, dropped_loops: list[Knitout_Loop]) -> None:
        self._dropped_loops = dropped_loops
        for loop in dropped_loops:
            loop.drop_from_bed(self)


class Directed_Instruction(Needle_Instruction):
    def __init__(self, needle: Needle_Specification, direction: str | Carriage_Pass_Direction, comment: str | None = None, **_kwargs: Any):
        super().__init__(needle=needle, comment=comment, **_kwargs)
        if direction is not None and isinstance(direction, str):
            direction = Carriage_Pass_Direction.get_direction(direction)
        self._direction: Carriage_Pass_Direction = direction

    @property
    def direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The direction that this instruction executes on.
        """
        return self._direction

    @property
    def _dir_str(self) -> str:
        return str(self.direction)


class Soft_Kick_Instruction(Directed_Instruction):
    """Marks kickbacks added in dat-complication process."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Kick

    def __init__(
        self,
        position: int | Needle_Specification,
        direction: str | Carriage_Pass_Direction,
        comment: str | None = None,
    ):
        """Initialize a kick instruction for a specific needle position.

        Args:
            position (int | Needle_Specification): The needle position for the kickback (must be between 0 and 540).
            direction (str | Carriage_Pass_Direction): The direction of the carriage pass.
            comment (str | None, optional): Optional comment for the instruction. Defaults to None.
        """
        self._position: int = int(position)
        super().__init__(needle=Needle_Position(is_front=True, position=self._position, is_slider=False), direction=direction, comment=comment)

    @property
    def position(self) -> int:
        """
        Returns:
            The position from the front bed to kick the carrier to.
        """
        return self._position

    def execute(self, machine_state: Knitting_Machine[Knitout_LoopT]) -> bool:
        """Soft kickbacks occur for things like releasehook management in dat files.

        Returns:
            True indicating the operation completed successfully.
        """
        return True


class Yarn_to_Needle_Instruction(Directed_Instruction):

    def __init__(self, needle: Needle_Specification, direction: str | Carriage_Pass_Direction, carrier_set: Yarn_Carrier_Set, comment: str | None = None, **_kwargs: Any):
        super().__init__(needle=needle, direction=direction, comment=comment, **_kwargs)
        self._carrier_set: Yarn_Carrier_Set = carrier_set

    @property
    def carrier_set(self) -> Yarn_Carrier_Set:
        """
        Returns:
            Yarn_Carrier_Set: The carrier_set that this instruction executes with.
        """
        return self._carrier_set

    @property
    def _carrier_str(self) -> str:
        return str(self._carrier_set)


class Miss_Instruction(Yarn_to_Needle_Instruction):
    """Instruction for positioning carriers above a needle without forming loops."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Miss

    def __init__(self, needle: Needle_Specification, direction: str | Carriage_Pass_Direction, carrier_set: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(needle, direction=direction, carrier_set=carrier_set, comment=comment)

    def execute(self, machine_state: Knitting_Machine[Knitout_LoopT]) -> bool:
        """Position the carrier above the given needle.

        Args:
            machine_state: The machine state to update.

        Returns:
            True indicating the operation completed successfully.
        """
        machine_state.miss(self.carrier_set, self.needle, self.direction)
        return True


class Knit_Pass_Instruction(Yarn_to_Needle_Instruction):

    def __init__(self, needle: Needle_Specification, direction: str | Carriage_Pass_Direction, carrier_set: Yarn_Carrier_Set, comment: str | None = None, **_kwargs: Any):
        super().__init__(needle=needle, direction=direction, carrier_set=carrier_set, comment=comment, **_kwargs)

    def compatible_in_carriage_pass(self, other_instruction: Needle_Instruction) -> bool:
        """
        All subclasses of Knit_Pass_Instructions can share a carriage pass (i.e., Knit and Tuck)

        Args:
            other_instruction (Needle_Instruction): The other instruction to test.

        Returns:
            bool: True if the other instruction can be performed in the same carriage pass as this instruction.
        """
        return isinstance(other_instruction, Knit_Pass_Instruction)


class Kick_Instruction(Knit_Pass_Instruction, Miss_Instruction):
    """Marks kickbacks added in dat-complication process."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Kick

    def __init__(
        self,
        position: int | Needle_Specification,
        direction: str | Carriage_Pass_Direction,
        carrier_set: Yarn_Carrier_Set,
        comment: str | None = None,
    ):
        """Initialize a kick instruction for a specific needle position.

        Args:
            position (int | Needle_Specification): The needle position for the kickback (must be between 0 and 540).
            direction (str | Carriage_Pass_Direction): The direction of the carriage pass.
            carrier_set (Yarn_Carrier_Set): The yarn carrier set to use.
            comment (str | None, optional): Optional comment for the instruction. Defaults to None.
        """
        self._position: int = int(position)
        super().__init__(needle=Needle_Position(is_front=True, position=self._position, is_slider=False), direction=direction, carrier_set=carrier_set, comment=comment)

    @property
    def position(self) -> int:
        """
        Returns:
            The position from the front bed to kick the carrier to.
        """
        return self._position


class Loop_Making_Instruction(Yarn_to_Needle_Instruction):
    """Base class for instructions that create loops."""

    _deepcopy_defaults: ClassVar[dict[str, Any]] = {"_moved_loops": []}

    def __init__(self, needle: Needle_Specification, direction: str | Carriage_Pass_Direction, carrier_set: Yarn_Carrier_Set, comment: str | None = None, **_kwargs: Any):
        super().__init__(needle=needle, direction=direction, carrier_set=carrier_set, comment=comment, **_kwargs)
        self._made_loops: list[Knitout_Loop] = []

    @property
    def made_loops(self) -> list[Knitout_Loop]:
        """
        Returns:
            list[Knitout_Loop]: The list of loops made by this instruction during its last execution.
        """
        return self._made_loops

    @made_loops.setter
    def made_loops(self, made_loops: list[Knitout_Loop]) -> None:
        """
        Sets this instruction to be the source instruction that formed the given loops.

        Args:
            made_loops (list[Knitout_Loop]): The loops created by this instruction.
        """
        self._made_loops = made_loops
        for l in made_loops:
            l.set_source(self)


class Knit_Instruction(Knit_Pass_Instruction, Loop_Making_Instruction, Dropping_Instruction):
    """Instruction for knitting a loop on a needle."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Knit

    def __init__(self, needle: Needle_Specification, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: str | None = None):
        super().__init__(needle=needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
        self.dropped_loops, self.made_loops = machine_state.knit(self.carrier_set, self.needle, self.direction)
        return self.effected_loops


class Tuck_Instruction(Knit_Pass_Instruction, Loop_Making_Instruction):
    """Instruction for tucking yarn on a needle without dropping existing loops."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Tuck

    def __init__(self, needle: Needle_Specification, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: str | None = None):
        super().__init__(needle=needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
        self.made_loops = machine_state.tuck(self.carrier_set, self.needle, self.direction)
        return self.effected_loops


class Two_Needle_Instruction(Needle_Instruction):
    def __init__(self, needle: Needle_Specification, needle_2: Needle_Specification, comment: str | None = None, **_kwargs: Any):
        super().__init__(needle=needle, comment=comment, **_kwargs)
        self._needle_2: Needle_Specification = needle_2
        self.loop_crossings_made: dict[Knitout_Loop, list[Knitout_Loop]] = {}  # Todo: Use loop crossing code.

    @property
    def needle_2(self) -> Needle_Specification:
        """
        Returns:
            Needle_Specification: The needle that loops are moved to.
        """
        return self._needle_2

    @property
    def moved_loops(self) -> list[Knitout_Loop]:
        """
        Returns:
            list[Knitout_Loop]: The list of loops moved by this instruction during its last execution.
        """
        return self._moved_loops

    @moved_loops.setter
    def moved_loops(self, loops: list[Knitout_Loop]) -> None:
        self._moved_loops = loops
        for l in loops:
            l.add_transfer_instruction(self)

    @property
    def implied_racking(self) -> None | int:
        """
        Returns:
            int | None: The racking required for this operation. None if no specific racking is required, or the required racking value to complete this operation.
        """
        racking = Knitting_Machine.get_transfer_rack(self.needle, self._needle_2)
        if racking is None:
            raise ValueError(f"No possible racking allows for {self}")
        return racking

    def _validate_aligned_needle(self, machine_state: Knitout_Knitting_Machine) -> None:
        """
        Validates that the aligned needle to the main needle of the instruction matches the given second needle in the instruction.
        Args:
            machine_state (Knitout_Knitting_Machine): The machine state to find the aligned needle for.

        Raises:
            ValueError: If the main needle is not aligned to the second needle in the instruction.
        """
        aligned_needle = machine_state.get_aligned_needle(self.needle, aligned_slider=self._needle_2.is_slider)
        if aligned_needle.position != self.needle_2.position and aligned_needle.is_front != self.needle_2.position:
            raise ValueError(f"Cannot {self.instruction_type.name} from {self.needle} to {self.needle_2} with racking {machine_state.rack}")

    def add_loop_crossing(self, left_loop: Knitout_Loop, right_loop: Knitout_Loop) -> None:
        """Update loop crossing to show transfers crossing loops.

        Args:
            left_loop: The left loop involved in the crossing.
            right_loop: The right loop involved in the crossing.
        """
        if left_loop not in self.loop_crossings_made:
            self.loop_crossings_made[left_loop] = []
        self.loop_crossings_made[left_loop].append(right_loop)

    @property
    def _n2_str(self) -> str:
        return str(self.needle_2)


class Split_Instruction(Loop_Making_Instruction, Two_Needle_Instruction):
    """Instruction for splitting a loop between two needles."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Split

    def __init__(
        self,
        needle: Needle_Specification,
        direction: Carriage_Pass_Direction | str,
        n2: Needle_Specification,
        cs: Yarn_Carrier_Set,
        comment: None | str = None,
    ):
        super().__init__(needle=needle, direction=direction, needle_2=n2, carrier_set=cs, comment=comment)
        self._needle_2: Needle_Specification = self._needle_2

    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
        self._validate_aligned_needle(machine_state)
        self.made_loops, self.moved_loops = machine_state.split(self.carrier_set, self.needle, self.direction)
        return self.effected_loops


class Xfer_Instruction(Two_Needle_Instruction):
    """Instruction for transferring loops between needles."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Xfer

    def __init__(self, needle: Needle_Specification, n2: Needle_Specification, comment: None | str = None):
        super().__init__(needle=needle, needle_2=n2, comment=comment)

    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
        self._validate_aligned_needle(machine_state)
        self.moved_loops = machine_state.xfer(self.needle, to_slider=self.needle_2.is_slider)
        return self.effected_loops


class Drop_Instruction(Dropping_Instruction):
    """Instruction for dropping loops from a needle."""

    instruction_type: ClassVar[Knitout_Instruction_Type] = Knitout_Instruction_Type.Drop

    def __init__(self, needle: Needle_Specification, comment: None | str = None):
        super().__init__(needle, comment=comment)

    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
        self.dropped_loops = machine_state.drop(self.needle)
        return self.effected_loops
