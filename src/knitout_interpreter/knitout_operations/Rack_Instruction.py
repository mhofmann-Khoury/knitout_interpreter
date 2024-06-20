"""Module for the Rack_Instruction class."""
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction, Knitout_Instruction_Type


class Rack_Instruction(Knitout_Instruction):

    def __init__(self, rack: float, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Rack, comment)
        self._rack_value: float = rack

    @property
    def rack(self) -> int:
        """
        :return: integer value of rack alignment.
        """
        return int(self._rack_value)

    @property
    def all_needle_rack(self) -> bool:
        """
        :return: True, if rack causes all-needle-knitting alignment.
        """
        return abs(self._rack_value - self.rack) != 0.0

    @property
    def rack_value(self) -> float:
        return self._rack_value

    def __str__(self):
        if not self.all_needle_rack:
            return f"{self.instruction_type} {int(self._rack_value)}{self.comment_str}"
        return f"{self.instruction_type} {self._rack_value}{self.comment_str}"

    def execute(self, machine_state: Knitting_Machine):
        if machine_state.rack == self.rack and machine_state.all_needle_rack == self.all_needle_rack:
            return False
        machine_state.rack = self._rack_value
        return True

    @staticmethod
    def rack_instruction_from_int_specification(rack: int = 0, all_needle_rack: bool = False, comment: None | str = None):
        """
        Note: From Knitout Specification:
        Number indicating the offset of the front bed relative to the back bed.
         That is, at racking R, back needle index B is aligned to front needle index B+R.
         Needles are considered aligned if they can transfer.
         That is, at racking 2, it is possible to transfer from f3 to b1.
         May be fractional on some machines. E.g., on Shima machines, 0.25/-0.75 are used for all-needle knitting.
        :return: Rack instruction given by integer racking and boolean all needle knitting alignment
        """
        rack_value: float = float(rack)
        if all_needle_rack:
            if rack_value < 0:
                rack_value -= 0.75
            else:
                rack_value += 0.25
        return Rack_Instruction(rack_value, comment)
