"""Basic tests of the Knitout Interpreter"""
from unittest import TestCase

from knit_graphs.Knit_Graph_Visualizer import visualize_knit_graph_safe
from resources.load_test_resources import load_test_resource

from knitout_interpreter import Knitout_Executer
from knitout_interpreter.knitout_operations import Knitout_Instruction_Type
from knitout_interpreter.run_knitout import run_knitout


class Test(TestCase):
    def test_run_knitout(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("single_knit.k"))
        print(execution)
        print(machine.front_loops())
        assert knit_graph.has_loop
        assert len(machine.front_loops()) == 1

    def test_multi_miss_line(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("multi_miss.k"))
        executer = Knitout_Executer(execution)
        executer.test_and_organize_instructions()
        assert len(executer.carriage_passes) == 3
        assert executer.carriage_passes[2].first_instruction.instruction_type == Knitout_Instruction_Type.Miss

    def test_stst_square(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("stst_square.k"))
        print(execution)
        print(machine.front_loops())
        visualize_knit_graph_safe(knit_graph)
        assert len(machine.front_loops()) == 4

    def test_tube(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("tube.k"))
        print(execution)
        print(f"Front Loops: {machine.front_loops()}")
        print(f"Back Loops: {machine.back_loops()}")
        print(f"In Front of Floats: {machine.carrier_system[1].yarn.loops_in_front_of_floats()}")
        print(f"Behind Floats: {machine.carrier_system[1].yarn.loops_behind_floats()}")
        visualize_knit_graph_safe(knit_graph, start_on_left=True)
        assert len(machine.front_loops()) == 2
        assert len(machine.back_loops()) == 2

    def test_rib(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("rib.k"))
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        visualize_knit_graph_safe(knit_graph)
        assert len(machine.front_loops()) == 2
        assert len(machine.back_loops()) == 1

    def test_split(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("split_pocket.k"))
        print(execution)
        print(f"Courses: {knit_graph.get_courses()}")
        print(f"Front Loops: {machine.front_loops()}")
        print(f"Back Loops: {machine.back_loops()}")
        print(f"In Front of Floats: {machine.carrier_system[1].yarn.loops_in_front_of_floats()}")
        print(f"Behind Floats: {machine.carrier_system[1].yarn.loops_behind_floats()}")
        visualize_knit_graph_safe(knit_graph, start_on_left=True)
        assert len(machine.front_loops()) == 4
        assert len(machine.back_loops()) == 4

    def test_lace(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("lace.k"))
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        print(knit_graph.get_courses())
        visualize_knit_graph_safe(knit_graph)
        assert len(knit_graph.get_courses()) == 4
        assert len(machine.front_loops()) == 5

    def test_jacquard(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("jacquard.k"))
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        print(knit_graph.get_courses())
        visualize_knit_graph_safe(knit_graph)

    def test_cable(self):
        execution, machine, knit_graph = run_knitout(load_test_resource("cable.k"))
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        print(knit_graph.get_courses())
        visualize_knit_graph_safe(knit_graph)
