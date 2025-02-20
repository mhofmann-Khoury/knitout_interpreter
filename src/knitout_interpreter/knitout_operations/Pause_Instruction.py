"""Module for the Pause Knitting Machine Instruction"""
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type, Knitout_Instruction


class Pause_Instruction(Knitout_Instruction):
    def __init__(self, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Pause, comment, interrupts_carriage_pass=False)

    def execute(self, machine_state):
        pass

    @staticmethod
    def execute_pause(machine_state: Knitting_Machine, comment: str | None = None):
        """
            :param machine_state: the current machine model to update
            :param comment: additional details to document in the knitout
            :return: the instruction
            """
        instruction = Pause_Instruction(comment)
        instruction.execute(machine_state)
        return instruction
