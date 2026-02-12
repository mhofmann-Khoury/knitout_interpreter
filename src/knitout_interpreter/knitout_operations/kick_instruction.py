"""Module containing the Kick_Instruction class."""

from __future__ import annotations

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Position, Needle_Specification
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction


class Kick_Instruction(Needle_Instruction):
    """Marks kickbacks added in dat-complication process."""

    def __init__(
        self,
        position: int | Needle_Specification,
        direction: str | Carriage_Pass_Direction,
        cs: Yarn_Carrier_Set | None = None,
        comment: str | None = None,
    ):
        """Initialize a kick instruction for a specific needle position.

        Args:
            position (int | Needle_Specification): The needle position for the kickback (must be between 0 and 540).
            direction (str | Carriage_Pass_Direction): The direction of the carriage pass.
            cs (Yarn_Carrier_Set, optional): The yarn carrier set to use. Defaults to None.
            comment (str | None, optional): Optional comment for the instruction. Defaults to None.
        """
        self._position: int = int(position)
        super().__init__(
            instruction_type=Knitout_Instruction_Type.Kick, needle=Needle_Position(is_front=True, position=self._position, is_slider=False), direction=direction, carrier_set=cs, comment=comment
        )
        self._direction: Carriage_Pass_Direction = self._direction

    @property
    def position(self) -> int:
        """
        Returns:
            The position from the front bed to kick the carrier to.
        """
        return self._position

    @property
    def no_carriers(self) -> bool:
        """
        Returns:
            bool: True if this is a soft-miss kickback with no carriers. False, otherwise
        """
        return self.carrier_set is None

    @property
    def carrier_set(self) -> Yarn_Carrier_Set | None:
        """

        Returns:
            Yarn_Carrier_Set | None: The yarn carrier set being kicked or None if this is a soft-miss kickback with no carriers (e.g., when doing a releasehook).
        """
        return self._carrier_set

    @property
    def direction(self) -> Carriage_Pass_Direction:
        return self._direction

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Position the carrier above the given front-bed needle position.

        Args:
            machine_state: The machine state to update.

        Returns:
            bool: True if the operation moved an active carrier, False otherwise.
        """
        self._test_operation()
        if self.carrier_set is not None:
            machine_state.miss(self.carrier_set, self.needle, self.direction)
            return True
        else:
            return False
