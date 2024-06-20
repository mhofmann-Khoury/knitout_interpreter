"""Module for the Pause Knitting Machine Instruction"""
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type, Knitout_Instruction


class Pause_Instruction(Knitout_Instruction):
    def __init__(self, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Pause, comment)

    def execute(self, machine_state):
        pass
