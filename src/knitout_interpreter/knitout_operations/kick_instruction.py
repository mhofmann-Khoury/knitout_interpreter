"""Module containing the Kick_Instruction class."""

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_operations.needle_instructions import Miss_Instruction


class Kick_Instruction(Miss_Instruction):
    """A subclass of the Miss_Instruction used to mark kickbacks added in dat-complication process."""

    def __init__(self, position: int, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set | None = None, comment: None | str = None):
        """Initialize a kick instruction for a specific needle position.

        Args:
            position: The needle position for the kickback (must be between 0 and 540).
            direction: The direction of the carriage pass.
            cs: The yarn carrier set to use. Defaults to None.
            comment: Optional comment for the instruction. Defaults to None.

        Raises:
            AssertionError: If position is not between 0 and 540.
        """
        assert 0 <= position <= 540, f"Cannot add a kickback beyond the bounds of the needle bed at position {position}"
        super().__init__(needle=Needle(is_front=True, position=position), direction=direction, cs=cs, comment=comment)

    @property
    def no_carriers(self) -> bool:
        """Check if this is a soft-miss kickback with no carriers.

        Returns:
            True if this is a soft-miss kickback with no carriers.
            No carriers can be set with a null carrier set or a carrier
            set with a 0 carrier (not a valid index for a carrier).
        """
        return self.carrier_set is None or 0 in self.carrier_set.carrier_ids
