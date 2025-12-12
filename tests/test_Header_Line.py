from unittest import TestCase

from resources.load_test_resources import load_test_resource
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Context import Knitout_Context


class TestKnitting_Machine_Header(TestCase):

    def test_read_header_from_executer(self):
        ko_context = Knitout_Context()
        codes, machine, knitgraph = ko_context.process_knitout_file(load_test_resource("short_header_test.k"))
        executer = Knitout_Executer(codes, Knitting_Machine())
