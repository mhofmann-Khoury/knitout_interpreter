from unittest import TestCase

from resources.load_test_resources import load_test_resource
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass, carriage_pass_of_instructions
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.needle_instructions import Knit_Instruction


class TestCarriage_Pass(TestCase):

    def test_all_needle_rightward_pass(self):
        cp = Carriage_Pass(
            Knit_Instruction(Needle(True, 1), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1)),
            0,
            all_needle_rack=True,
        )
        back_knit = Knit_Instruction(Needle(False, 1), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1))
        self.assertTrue(cp.can_add_instruction(back_knit, 0, True))
        cp.add_instruction(back_knit, 0, True)
        self.assertTrue(len(cp) == 2)

    def test_all_needle_racked(self):
        codes = parse_knitout(load_test_resource("all_needle_racked.k"), pattern_is_file=True)
        executer = Knitout_Executer(codes)
        for carriage_pass in executer.carriage_passes:
            self.assertGreater(len(carriage_pass), 2, f"Found a shortened carriage pass {carriage_pass}")

    def test_add_kicks_to_end(self):
        knits = [Knit_Instruction(Needle(True, i), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1)) for i in range(1, 4)]
        cp = carriage_pass_of_instructions(knits)
        kicks = [Kick_Instruction(5, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1))]
        cp.add_kicks(kicks)
        self.assertTrue(isinstance(cp.last_instruction, Kick_Instruction))
        self.assertEqual(cp.last_needle.position, 5)

        knits = [Knit_Instruction(Needle(True, i), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(1)) for i in range(4, 1, -1)]
        cp = carriage_pass_of_instructions(knits)
        kicks = [Kick_Instruction(1, Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(1))]
        cp.add_kicks(kicks)
        self.assertTrue(isinstance(cp.last_instruction, Kick_Instruction))
        self.assertEqual(cp.last_needle.position, 1)

        cp = carriage_pass_of_instructions(knits)
        kicks = [Kick_Instruction(5, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(2))]
        try:
            cp.add_kicks(kicks)
            self.fail("Kick with wrong carrier should raise value error.")
        except ValueError as _e:
            pass

    def test_inject_kicks(self):
        knits = [Knit_Instruction(Needle(True, i), Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1)) for i in range(2, 6, 2)]
        cp = carriage_pass_of_instructions(knits)
        kicks = [Kick_Instruction(i, Carriage_Pass_Direction.Rightward, Yarn_Carrier_Set(1)) for i in range(1, 7, 2)]
        cp.add_kicks(kicks)
        for i in range(1, 7, 2):
            kick = cp.instruction_by_slot(i)
            self.assertTrue(isinstance(kick, Kick_Instruction))
