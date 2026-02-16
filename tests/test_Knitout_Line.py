import copy
from unittest import TestCase

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Position
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import Violation, ViolationAction, ViolationResponse

from knitout_interpreter.knitout_execution_structures.Knitout_Knitting_Machine import Knitout_Knitting_Machine
from knitout_interpreter.knitout_execution_structures.knitout_loops import Knitout_Loop
from knitout_interpreter.knitout_operations.Header_Line import Knitout_Version_Line
from knitout_interpreter.knitout_operations.needle_instructions import Tuck_Instruction


class TestKnitout_Line(TestCase):

    def test_deep_copy_simple_type(self):
        version_line = Knitout_Version_Line(version=2)
        version_line.original_line_number = 1
        version_line.line_number = 2
        copy_line = copy.deepcopy(version_line)
        self.assertTrue(isinstance(copy_line, Knitout_Version_Line))
        self.assertEqual(version_line.version, copy_line.version)
        self.assertLess(version_line._creation_time, copy_line._creation_time)
        self.assertIsNone(copy_line.original_line_number)
        self.assertIsNone(copy_line.line_number)
        self.assertEqual(1, version_line.original_line_number)
        self.assertEqual(2, version_line.line_number)

    def test_deep_copy_tuck(self):
        comment = "comment"
        tuck_line = Tuck_Instruction(Needle_Position(True, 1, is_slider=False), Carriage_Pass_Direction.Leftward, Yarn_Carrier_Set(1), comment)
        knitting_machine = Knitout_Knitting_Machine[Knitout_Loop]()
        knitting_machine.set_response_for(Violation.INACTIVE_CARRIER, ViolationResponse(ViolationAction.IGNORE, proceed_with_operation=True))
        tuck_line.execute(knitting_machine)
        self.assertEqual(1, len(tuck_line.made_loops))
        copy_line = copy.deepcopy(tuck_line)
        self.assertTrue(isinstance(copy_line, Tuck_Instruction))
        self.assertEqual(tuck_line.needle, copy_line.needle)
        self.assertEqual(tuck_line.comment, copy_line.comment)
        self.assertLess(tuck_line._creation_time, copy_line._creation_time)
        self.assertEqual(0, len(copy_line.made_loops))
