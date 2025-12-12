"""Basic tests of the Knitout Interpreter"""

from unittest import TestCase

from resources.load_test_resources import load_test_resource

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction_Type
from knitout_interpreter.run_knitout import run_knitout


class Test(TestCase):
    def test_run_knitout(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("single_knit.k"))
        assert knit_graph.has_loop
        assert len(machine.front_loops()) == 1
        self.assertEqual(len(execution), 9)

    def test_merge_cp(self):
        codes = parse_knitout(load_test_resource("merge_cp.k"), pattern_is_file=True)
        executer = Knitout_Executer(codes)
        self.assertEqual(executer.execution_time, 5)

    def test_multi_miss_line(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("multi_miss.k"))
        executer = Knitout_Executer(execution)
        executer.test_and_organize_instructions()
        assert len(executer.carriage_passes) == 4
        assert executer.carriage_passes[3].first_instruction.instruction_type == Knitout_Instruction_Type.Miss

    def test_stst_square(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("stst_square.k"))
        assert len(machine.front_loops()) == 4

    def test_tube(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("tube.k"))
        assert len(machine.front_loops()) == 2
        assert len(machine.back_loops()) == 2

    def test_rib(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("rib.k"))
        assert len(machine.front_loops()) == 2
        assert len(machine.back_loops()) == 1

    def test_split(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("split_pocket.k"))
        assert len(machine.front_loops()) == 4
        assert len(machine.back_loops()) == 4

    def test_lace(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("lace.k"))
        assert len(knit_graph.get_courses()) == 4
        assert len(machine.front_loops()) == 5

    def test_jacquard(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("jacquard.k"))

    def test_cable(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("cable.k"))
