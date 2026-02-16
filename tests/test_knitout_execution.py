from unittest import TestCase

from resources.load_test_resources import load_test_resource
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Position

from knitout_interpreter.debugger.knitout_debugger import Knitout_Debugger
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type
from knitout_interpreter.run_knitout import run_knitout


class TestKnitout_Executer(TestCase):

    def setUp(self):
        """
        Modify this code with the knitout debugger preferences desired.
        """
        self.debugger = Knitout_Debugger()

    def test_snapshots(self):
        snapshot_targets = {6, 8, 27, 28}
        executer = Knitout_Executer(load_test_resource("stst_square.k"), debugger=self.debugger, snapshot_targets=snapshot_targets)
        for t in snapshot_targets:
            self.assertIn(t, executer.snapshots)
        snapshot = executer.snapshots[6]
        self.assertIsNone(snapshot.last_loop_id)
        self.assertFalse(snapshot.carrier_system.inserting_hook_available)
        self.assertEqual(int(snapshot.carrier_system.hooked_carrier), 1)
        snapshot = executer.snapshots[8]
        self.assertEqual(snapshot.last_loop_id, 1)
        self.assertFalse(snapshot.carrier_system.inserting_hook_available)
        self.assertEqual(int(snapshot.carrier_system.hooked_carrier), 1)
        self.assertEqual(len(snapshot.front_loops()), 2)
        self.assertIn(Needle_Position(True, 3, is_slider=False), snapshot)
        self.assertIn(Needle_Position(True, 4, is_slider=False), snapshot)
        snapshot = executer.snapshots[27]
        self.assertTrue(snapshot.carrier_system.inserting_hook_available)
        self.assertTrue(snapshot.carrier_system.is_active([1]))
        self.assertEqual(len(snapshot.front_loops()), 4)
        snapshot = executer.snapshots[28]
        self.assertTrue(snapshot.carrier_system.inserting_hook_available)
        self.assertFalse(snapshot.carrier_system.is_active([1]))

    def test_run_knitout(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("single_knit.k"), debugger=self.debugger)
        self.assertTrue(knit_graph.has_loop)
        self.assertEqual(len(machine.front_loops()), 1)
        self.assertEqual(len(execution), 9)

    def test_merge_cp(self):
        executer = Knitout_Executer(load_test_resource("merge_cp.k"), debugger=self.debugger)
        self.assertEqual(executer.execution_time, 5)

    def test_multi_miss_line(self):
        executer = Knitout_Executer(load_test_resource("multi_miss.k"), debugger=self.debugger)
        self.assertEqual(executer.execution_time, 4)
        self.assertIs(executer.carriage_passes[3].first_instruction.instruction_type, Knitout_Instruction_Type.Miss)

    def test_stst_square(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("stst_square.k"), debugger=self.debugger)
        self.assertEqual(len(machine.front_loops()), 4)

    def test_tube(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("tube.k"), debugger=self.debugger)
        self.assertEqual(len(machine.front_loops()), 2)
        self.assertEqual(len(machine.back_loops()), 2)

    def test_rib(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("rib.k"), debugger=self.debugger)
        self.assertEqual(len(machine.front_loops()), 2)
        self.assertEqual(len(machine.back_loops()), 1)

    def test_split(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("split_pocket.k"), debugger=self.debugger)
        self.assertEqual(len(machine.front_loops()), 4)
        self.assertEqual(len(machine.back_loops()), 4)

    def test_lace(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("lace.k"), debugger=self.debugger)
        self.assertEqual(len(knit_graph.get_courses()), 4)
        self.assertEqual(len(machine.front_loops()), 5)

    def test_jacquard(self):
        run_knitout(load_test_resource("jacquard.k"), debugger=self.debugger)

    def test_cable(self):
        run_knitout(load_test_resource("cable.k"), debugger=self.debugger)
