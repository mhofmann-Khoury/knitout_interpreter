"""Test cases for the knitout debugger."""

from unittest import TestCase

from resources.load_test_resources import load_test_resource
from virtual_knitting_machine.machine_components.needles.Needle import Needle

from knitout_interpreter.knitout_debugger.common_debugging_conditions import is_instruction_type, loop_count_exceeds
from knitout_interpreter.knitout_debugger.knitout_debugger import Knitout_Debugger
from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_operations.carrier_instructions import Hook_Instruction


class TestKnitout_Debugger(TestCase):

    def test_step_debugger(self):
        debugger = Knitout_Debugger()
        debugger.step()
        _executer = Knitout_Executer(load_test_resource("single_knit.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 4)

    def test_condition_bp(self):
        debugger = Knitout_Debugger()
        debugger.step()
        debugger.enable_step_condition("is_hook", lambda d, i: is_instruction_type(d, i, Hook_Instruction))  # Should stop on 7, 17, 18
        debugger.enable_step_condition("5 loops", lambda d, i: loop_count_exceeds(d, i, 5), is_carriage_pass_step=True)  # should not stop because not in step_continue mode
        _executer = Knitout_Executer(load_test_resource("rib.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 3)
        self.assertIn(7, debugger.machine_snapshots)
        self.assertIn(17, debugger.machine_snapshots)
        self.assertIn(18, debugger.machine_snapshots)

    def test_condition_cp_bp(self):
        debugger = Knitout_Debugger()
        debugger.step_carriage_pass()
        debugger.enable_step_condition("is_hook", lambda d, i: is_instruction_type(d, i, Hook_Instruction))  # Should not stop because in carriage pass mode
        debugger.enable_step_condition("5 loops", lambda d, i: loop_count_exceeds(d, i, 4), is_carriage_pass_step=True)  # should stop on 14
        _executer = Knitout_Executer(load_test_resource("rib.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 1)
        self.assertIn(14, debugger.machine_snapshots)

    def test_step_cp_debugger(self):
        debugger = Knitout_Debugger()
        debugger.step_carriage_pass()
        _executer = Knitout_Executer(load_test_resource("single_knit.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 1)
        self.assertIn(8, debugger.machine_snapshots)

        debugger = Knitout_Debugger()
        debugger.step_carriage_pass()
        _executer = Knitout_Executer(load_test_resource("stst_square.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 5)

    def test_bp_set_debugger(self):
        debugger = Knitout_Debugger()
        debugger.continue_knitout()
        debugger.enable_breakpoint(8)
        debugger.enable_breakpoint(9)
        debugger.enable_breakpoint(29)
        _executer = Knitout_Executer(load_test_resource("stst_square.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 3)
        self.assertIn(8, debugger.machine_snapshots)
        self.assertIn(9, debugger.machine_snapshots)
        self.assertIn(29, debugger.machine_snapshots)
        snapshot_8 = debugger.machine_snapshots[8]
        self.assertEqual(len(snapshot_8.all_active_needles), 0)
        self.assertFalse(snapshot_8.carrier_system.inserting_hook_available)
        snapshot_9 = debugger.machine_snapshots[9]
        self.assertTrue(Needle(is_front=True, position=4) in snapshot_9)
        self.assertFalse(snapshot_9.carrier_system.inserting_hook_available)
        snapshot_29 = debugger.machine_snapshots[29]
        for n in range(1, 5):
            self.assertTrue(Needle(is_front=True, position=n) in snapshot_29)
        self.assertTrue(snapshot_29.carrier_system.inserting_hook_available)

    def test_bp_mid_cp(self):
        debugger = Knitout_Debugger()
        debugger.step_carriage_pass()
        debugger.enable_breakpoint(10)
        _executer = Knitout_Executer(load_test_resource("stst_square.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 6)
        self.assertIn(10, debugger.machine_snapshots)
        snapshot = debugger.machine_snapshots[10]
        for n in range(3, 5):
            self.assertTrue(Needle(is_front=True, position=n) in snapshot)

    def test_bp_from_knitout(self):
        debugger = Knitout_Debugger()
        debugger.continue_knitout()
        _executer = Knitout_Executer(load_test_resource("knitout_with_bp.k"), debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 2)
        self.assertIn(8, debugger.machine_snapshots)
        self.assertIn(10, debugger.machine_snapshots)

    def test_bp_on_error(self):
        debugger = Knitout_Debugger()
        debugger.continue_knitout()
        try:
            _executer = Knitout_Executer(load_test_resource("bp_on_error.k"), debugger=debugger)
        except Knitout_Machine_StateError as _e:
            pass
        self.assertEqual(len(debugger.machine_snapshots), 1)
        self.assertIn(7, debugger.machine_snapshots)
