from unittest import TestCase

from resources.load_test_resources import load_test_resource

from knitout_interpreter.debugger.knitout_debugger import Knitout_Debugger
from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.run_knitout import run_knitout


class TestKnitout_Executer(TestCase):

    def setUp(self):
        """
        Modify this code with the knitout debugger preferences desired.
        """
        self.debugger = Knitout_Debugger()

    def test_raise_machine_error(self):
        with self.assertRaises(Knitout_Machine_StateError):
            execution, machine, knit_graph = run_knitout(load_test_resource("bad_ko.k"))
