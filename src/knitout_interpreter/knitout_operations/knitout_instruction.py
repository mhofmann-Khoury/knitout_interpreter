"""Structure for Instructions"""

from __future__ import annotations

from enum import Enum

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Instruction_Type(Enum):
    """Enumeration of knitout instruction types."""

    In = "in"
    Inhook = "inhook"
    Releasehook = "releasehook"
    Out = "out"
    Outhook = "outhook"
    Stitch = "stitch"
    Rack = "rack"
    Knit = "knit"
    Tuck = "tuck"
    Split = "split"
    Drop = "drop"
    Xfer = "xfer"
    Miss = "miss"
    Kick = "kick"
    Pause = "pause"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def get_instruction(inst_str: str) -> Knitout_Instruction_Type:
        """Get the instruction type from a string.

        Args:
            inst_str (str): Instruction string to convert.

        Returns:
            Knitout_Instruction_Type: The corresponding Knitout_Instruction_Type enum value.
        """
        return Knitout_Instruction_Type[inst_str.capitalize()]

    @property
    def is_carrier_instruction(self) -> bool:
        """Check if instruction operates on yarn carriers.

        Returns:
            bool: True if instruction operates on yarn carriers.
        """
        return self in [
            Knitout_Instruction_Type.In,
            Knitout_Instruction_Type.Inhook,
            Knitout_Instruction_Type.Releasehook,
            Knitout_Instruction_Type.Out,
            Knitout_Instruction_Type.Outhook,
        ]

    @property
    def is_needle_instruction(self) -> bool:
        """Check if instruction operates on needles.

        Returns:
            bool: True if operation operates on needles.
        """
        return self in [
            Knitout_Instruction_Type.Knit,
            Knitout_Instruction_Type.Tuck,
            Knitout_Instruction_Type.Split,
            Knitout_Instruction_Type.Drop,
            Knitout_Instruction_Type.Xfer,
            Knitout_Instruction_Type.Kick,
            Knitout_Instruction_Type.Miss,
        ]

    @property
    def is_loop_making_instruction(self) -> bool:
        """Check if instruction operates on needles.

        Returns:
            bool: True if operation creates a loop on the first needle in the instruction.
        """
        return self in [
            Knitout_Instruction_Type.Knit,
            Knitout_Instruction_Type.Tuck,
            Knitout_Instruction_Type.Split,
        ]

    @property
    def is_miss_instruction(self) -> bool:
        """
        Returns:
            bool: True if the operation is a miss and can occur in a miss instruction pass.
        """
        return self is Knitout_Instruction_Type.Miss

    @property
    def in_knitting_pass(self) -> bool:
        """
        Returns:
            bool: True if instruction can be done in a knit pass. False otherwise.
        """
        return self in [Knitout_Instruction_Type.Knit, Knitout_Instruction_Type.Tuck, Knitout_Instruction_Type.Kick]

    @property
    def all_needle_instruction(self) -> bool:
        """
        Returns:
            bool: True if instruction is compatible with all-needle knitting. False, otherwise.
        """
        return self.in_knitting_pass

    @property
    def directed_pass(self) -> bool:
        """
        Returns:
            bool: True if instruction requires a direction. False, otherwise.
        """
        return self in [
            Knitout_Instruction_Type.Knit,
            Knitout_Instruction_Type.Tuck,
            Knitout_Instruction_Type.Miss,
            Knitout_Instruction_Type.Split,
            Knitout_Instruction_Type.Kick,
        ]

    @property
    def requires_carrier(self) -> bool:
        """
        Returns:
            bool: True if instruction requires a carrier. False, otherwise.
        """
        return self in [
            Knitout_Instruction_Type.Knit,
            Knitout_Instruction_Type.Tuck,
            Knitout_Instruction_Type.Miss,
            Knitout_Instruction_Type.Split,
        ]

    @property
    def requires_second_needle(self) -> bool:
        """
        Returns:
            bool: True if instruction requires a second needle. False, otherwise.
        """
        return self in [Knitout_Instruction_Type.Xfer, Knitout_Instruction_Type.Split]

    @property
    def allow_sliders(self) -> bool:
        """
        Returns:
            bool: True if this is a transfer instruction that can operate on sliders. False, otherwise.
        """
        return self is Knitout_Instruction_Type.Xfer

    def compatible_pass(self, other_instruction: Knitout_Instruction_Type) -> bool:
        """Determine if instruction can share a machine pass with another instruction.

        Args:
            other_instruction (Knitout_Instruction_Type): The other instruction to check compatibility with.

        Returns:
            bool: True if both instructions could be executed in the same pass.
        """
        return (self.is_miss_instruction and other_instruction.is_miss_instruction) or (self.in_knitting_pass and other_instruction.in_knitting_pass) or self is other_instruction


class Knitout_Instruction(Knitout_Line):
    """Superclass for knitout operations."""

    def __init__(self, instruction_type: Knitout_Instruction_Type, comment: str | None, interrupts_carriage_pass: bool = True):
        super().__init__(comment, interrupts_carriage_pass=interrupts_carriage_pass)
        self._instruction_type: Knitout_Instruction_Type = instruction_type

    @property
    def instruction_type(self) -> Knitout_Instruction_Type:
        """
        Returns:
            Knitout_Instruction_Type: The instruction type of this instruction.
        """
        return self._instruction_type

    def __str__(self) -> str:
        return f"{self.instruction_type}{self.comment_str}"

    def will_update_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """
        Args:
            machine_state (Knitting_Machine): The machine state to test if this instruction will update it.

        Returns:
            bool: True if this instruction will update the machine state. False, otherwise.
        """
        return True

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Execute the instruction on the machine state.

        Args:
            machine_state (Knitting_Machine): The machine state to update.

        Returns:
            bool: True if the process completes an update to the machine state. False, otherwise.
        """
        return False
