"""Module containing the Knitout_Loop subclass of Machine_Knit_Loop"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from knit_graphs.Loop import Loop
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import Machine_Knit_Loop
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn

if TYPE_CHECKING:
    from knitout_interpreter.knitout_operations.needle_instructions import Dropping_Instruction, Loop_Making_Instruction, Two_Needle_Instruction


class Knitout_Loop(Machine_Knit_Loop):

    def __init__(self, source_needle: Needle[Self], yarn: Machine_Knit_Yarn[Self], **_loop_kwargs: Any) -> None:
        super().__init__(source_needle, yarn)
        self._source_instruction: Loop_Making_Instruction | None = None
        self._transfer_history: list[Two_Needle_Instruction] = []
        self._dropping_instruction: Dropping_Instruction | None = None

    @property
    def source_instruction(self) -> Loop_Making_Instruction:
        """
        Returns:
            Loop_Making_Instruction: The instruction that formed this loop.

        Raises:
            ValueError: If the source instruction was not set.
        """
        if self._source_instruction is None:
            raise ValueError("Source Instruction was not set for this loop")
        return self._source_instruction

    @property
    def dropping_instruction(self) -> Dropping_Instruction | None:
        """
        Returns:
            Drop_Instruction | Knit_Instruction | None: The instruction that dropped this loop from the needle bed or None if the loop is still active.
        """
        return self._dropping_instruction

    @property
    def last_instruction(self) -> Dropping_Instruction | Two_Needle_Instruction | Loop_Making_Instruction:
        """
        Returns:
            Dropping_Instruction | Two_Needle_Instruction | Loop_Making_Instruction: The last instruction to operate on this loop.
        """
        if self.dropping_instruction is not None:
            return self.dropping_instruction
        elif len(self._transfer_history) > 0:
            return self._transfer_history[-1]
        else:
            return self.source_instruction

    @property
    def forming_carriage_direction(self) -> Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction: The direction that this loop was formed in.
        """
        return self.source_instruction.direction

    def set_source(self, instruction: Loop_Making_Instruction) -> None:
        """

        Args:
            instruction (Loop_Making_Instruction): The instruction that formed this loop.

        Raises:
            ValueError: If this is called when a source instruction is already known
        """
        if self._source_instruction is not None:
            raise ValueError("Can only set the source instruction once per loop")
        self._source_instruction = instruction

    def add_transfer_instruction(self, xfer: Two_Needle_Instruction) -> None:
        """
        Adds the given split or xfer to the transfer history of this loop.
        Args:
            xfer (Two_Needle_Instruction): The split or xfer to be added to the transfer history of this loop.
        """
        self._transfer_history.append(xfer)

    def drop_from_bed(self, drop: Dropping_Instruction) -> None:
        """
        Sets the instruction that drops this loop from the needle bed.
        Args:
            drop (Drop_Instruction | Knit_Instruction): The instruction that caused the loop to drop from the needle bed.

        Raises:
            ValueError: If this loop as already dropped from the needle bed.
        """
        if self.dropping_instruction is not None:
            raise ValueError("Can only drop a loop from the needle bed once.")
        self._dropping_instruction = drop

    def __lt__(self, other: Loop | int) -> bool:
        """Compare loop_id with another loop or integer for ordering.

        Args:
            other (Loop | int): The other loop or integer to compare with.

        Returns:
            bool: True if this loop's id is less than the other's id.
        """
        if isinstance(other, int):
            return self.loop_id < other
        elif (
            isinstance(other, Knitout_Loop)
            and self._source_instruction is not None
            and other._source_instruction is not None
            and self.source_instruction.line_number is not None
            and other.source_instruction.line_number is not None
        ):
            return self.source_instruction.line_number < other.source_instruction.line_number
        else:
            return self.loop_id < other.loop_id
