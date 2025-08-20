from unittest import TestCase

from resources.load_test_resources import load_test_resource
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.needle_instructions import Knit_Instruction


class TestCarriage_Pass(TestCase):

    def test_all_needle_rightward_pass(self):
        cp = Carriage_Pass(Knit_Instruction(Needle(True, 1), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1)), 0, all_needle_rack=True)
        back_knit = Knit_Instruction(Needle(False, 1), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1))
        self.assertTrue(cp.can_add_instruction(back_knit, 0, True))
        cp.add_instruction(back_knit, 0, True)
        self.assertTrue(len(cp) == 2)

    def test_all_needle_racked(self):
        codes = parse_knitout(load_test_resource('all_needle_racked.k'), pattern_is_file=True)
        executer = Knitout_Executer(codes)
        for carriage_pass in executer.carriage_passes:
            assert len(carriage_pass) > 2, f'Found a shortened carriage pass {carriage_pass}'
