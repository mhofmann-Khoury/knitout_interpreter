"""Test cases for the knitout debugger."""

from unittest import TestCase

from resources.load_test_resources import load_test_resource
from virtual_knitting_machine.machine_components.needles.Needle import Needle

from knitout_interpreter.knitout_debugger.knitout_debugger import Knitout_Debugger
from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout


class TestKnitout_Debugger(TestCase):

    def test_step_debugger(self):
        debugger = Knitout_Debugger()
        debugger.step()
        codes = parse_knitout(load_test_resource("single_knit.k"), pattern_is_file=True)
        _executer = Knitout_Executer(codes, debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 4)

    def test_step_cp_debugger(self):
        debugger = Knitout_Debugger()
        debugger.step_carriage_pass()
        codes = parse_knitout(load_test_resource("single_knit.k"), pattern_is_file=True)
        _executer = Knitout_Executer(codes, debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 1)
        self.assertIn(8, debugger.machine_snapshots)

        debugger = Knitout_Debugger()
        debugger.step_carriage_pass()
        codes = parse_knitout(load_test_resource("stst_square.k"), pattern_is_file=True)
        _executer = Knitout_Executer(codes, debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 5)

    def test_bp_set_debugger(self):
        debugger = Knitout_Debugger()
        debugger.continue_knitout()
        debugger.set_breakpoint(8)
        debugger.set_breakpoint(9)
        debugger.set_breakpoint(29)
        codes = parse_knitout(load_test_resource("stst_square.k"), pattern_is_file=True)
        _executer = Knitout_Executer(codes, debugger=debugger)
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
        debugger.set_breakpoint(10)
        codes = parse_knitout(load_test_resource("stst_square.k"), pattern_is_file=True)
        _executer = Knitout_Executer(codes, debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 6)
        self.assertIn(10, debugger.machine_snapshots)
        snapshot = debugger.machine_snapshots[10]
        for n in range(3, 5):
            self.assertTrue(Needle(is_front=True, position=n) in snapshot)

    def test_bp_from_knitout(self):
        debugger = Knitout_Debugger()
        debugger.continue_knitout()
        codes = parse_knitout(load_test_resource("knitout_with_bp.k"), pattern_is_file=True)
        _executer = Knitout_Executer(codes, debugger=debugger)
        self.assertEqual(len(debugger.machine_snapshots), 2)
        self.assertIn(8, debugger.machine_snapshots)
        self.assertIn(10, debugger.machine_snapshots)

    def test_bp_on_error(self):
        debugger = Knitout_Debugger()
        debugger.continue_knitout()
        codes = parse_knitout(load_test_resource("bp_on_error.k"), pattern_is_file=True)
        try:
            _executer = Knitout_Executer(codes, debugger=debugger)
        except Knitout_Machine_StateError as _e:
            pass
        self.assertEqual(len(debugger.machine_snapshots), 1)
        self.assertIn(7, debugger.machine_snapshots)
