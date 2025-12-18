from unittest import TestCase

from resources.load_test_resources import load_test_resource

from knitout_interpreter.knitout_execution import Knitout_Executer


class TestKnitting_Machine_Header(TestCase):

    def test_read_header_from_executer(self):
        executer = Knitout_Executer(load_test_resource("short_header_test.k"))
