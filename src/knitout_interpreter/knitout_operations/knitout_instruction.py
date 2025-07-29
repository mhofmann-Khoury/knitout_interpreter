"""Structure for Instructions"""
from __future__ import annotations
from enum import Enum

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Instruction_Type(Enum):
    """
        Knitout Instruction types
    """
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
        """
        Get the instruction from a string
        :param inst_str: instruction string to pull from
        :return: Instruction_Type Enum of that type
        """
        return Knitout_Instruction_Type[inst_str.capitalize()]

    @property
    def is_carrier_instruction(self) -> bool:
        """
        :return: True if instruction operates on yarn carriers
        """
        return self in [Knitout_Instruction_Type.In, Knitout_Instruction_Type.Inhook,
                        Knitout_Instruction_Type.Releasehook,
                        Knitout_Instruction_Type.Out, Knitout_Instruction_Type.Outhook]

    @property
    def is_needle_instruction(self) -> bool:
        """
        :return: True if operation operates on needles
        """
        return self in [Knitout_Instruction_Type.Knit, Knitout_Instruction_Type.Tuck, Knitout_Instruction_Type.Split,
                        Knitout_Instruction_Type.Drop, Knitout_Instruction_Type.Xfer, Knitout_Instruction_Type.Kick]

    @property
    def in_knitting_pass(self) -> bool:
        """
        :return: True if instruction can be done in a knit pass
        """
        return self in [Knitout_Instruction_Type.Knit, Knitout_Instruction_Type.Tuck, Knitout_Instruction_Type.Kick]

    @property
    def all_needle_instruction(self) -> bool:
        """
        :return: True if instruction is compatible with all-needle knitting
        """
        return self.in_knitting_pass

    @property
    def directed_pass(self) -> bool:
        """
        :return: True if instruction requires a direction
        """
        return self in [Knitout_Instruction_Type.Knit, Knitout_Instruction_Type.Tuck, Knitout_Instruction_Type.Miss, Knitout_Instruction_Type.Split, Knitout_Instruction_Type.Kick]

    @property
    def requires_carrier(self) -> bool:
        """
        :return: True if instruction requires a direction
        """
        return self.directed_pass

    @property
    def requires_second_needle(self) -> bool:
        """
        :return: True if instruction requires second needle
        """
        return self in [Knitout_Instruction_Type.Xfer, Knitout_Instruction_Type.Split]

    @property
    def allow_sliders(self) -> bool:
        """
        :return: True if a xfer instruction that can operate on sliders
        """
        return self is Knitout_Instruction_Type.Xfer

    def compatible_pass(self, other_instruction: Knitout_Instruction_Type) -> bool:
        """
        Determine if instruction can share a machine pass.
        :param other_instruction: Needle_Instruction to see if they match the pass type.
        :return: True if both instructions could be executed in a pass.
        """
        if not self.is_needle_instruction:
            return False
        elif self.in_knitting_pass and other_instruction.in_knitting_pass:
            return True
        else:
            return self is other_instruction


class Knitout_Instruction(Knitout_Line):
    """
        Superclass for knitout operations
    """

    def __init__(self, instruction_type: Knitout_Instruction_Type, comment: str | None, interrupts_carriage_pass: bool=True):
        super().__init__(comment, interrupts_carriage_pass=interrupts_carriage_pass)
        self.instruction_type: Knitout_Instruction_Type = instruction_type

    def __str__(self) -> str:
        return f"{self.instruction_type}{self.comment_str}"

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """
        Executes the instruction on the machine state.
        :param machine_state: The machine state to update.
        :return: True if the process completes an update.
        """
        return False
