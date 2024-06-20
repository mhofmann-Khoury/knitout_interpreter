"""Basic tests of the Knitout Interpreter"""
from unittest import TestCase

from knit_graphs.knit_graph_visualizer.Stitch_Visualizer import visualize_stitches

from knitout_interpreter.knitout_language.Knitout_Context import run_knitout


class Test(TestCase):
    def test_run_knitout(self):
        execution, machine, knit_graph = run_knitout("single_knit.k")
        print(execution)
        print(machine.front_loops())
        assert knit_graph.has_loop
        assert len(machine.front_loops()) == 1

    def test_stst_square(self):
        execution, machine, knit_graph = run_knitout("stst_square.k")
        print(execution)
        print(machine.front_loops())
        visualize_stitches(knit_graph)
        assert len(machine.front_loops()) == 4

    def test_tube(self):
        execution, machine, knit_graph = run_knitout("tube.k")
        print(execution)
        print(f"Front Loops: {machine.front_loops()}")
        print(f"Back Loops: {machine.back_loops()}")
        print(f"In Front of Floats: {machine.carrier_system[1].yarn.loops_in_front_of_floats()}")
        print(f"Behind Floats: {machine.carrier_system[1].yarn.loops_behind_floats()}")
        visualize_stitches(knit_graph, start_on_left=True)
        assert len(machine.front_loops()) == 2
        assert len(machine.back_loops()) == 2

    def test_rib(self):
        execution, machine, knit_graph = run_knitout("rib.k")
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        visualize_stitches(knit_graph)
        assert len(machine.front_loops()) == 2
        assert len(machine.back_loops()) == 1

    def test_split(self):
        execution, machine, knit_graph = run_knitout("split_pocket.k")
        print(execution)
        print(f"Courses: {knit_graph.get_courses()}")
        print(f"Front Loops: {machine.front_loops()}")
        print(f"Back Loops: {machine.back_loops()}")
        print(f"In Front of Floats: {machine.carrier_system[1].yarn.loops_in_front_of_floats()}")
        print(f"Behind Floats: {machine.carrier_system[1].yarn.loops_behind_floats()}")
        visualize_stitches(knit_graph, start_on_left=True)
        assert len(machine.front_loops()) == 4
        assert len(machine.back_loops()) == 4

    def test_lace(self):
        execution, machine, knit_graph = run_knitout("lace.k")
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        print(knit_graph.get_courses())
        visualize_stitches(knit_graph)
        assert len(knit_graph.get_courses()) == 4
        assert len(machine.front_loops()) == 5

    def test_jacquard(self):
        execution, machine, knit_graph = run_knitout("jacquard.k")
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        print(knit_graph.get_courses())
        visualize_stitches(knit_graph)

    def test_cable(self):
        execution, machine, knit_graph = run_knitout("cable.k")
        print(execution)
        print(machine.front_loops())
        print(machine.back_loops())
        print(knit_graph.get_courses())
        visualize_stitches(knit_graph)
