from unittest import TestCase

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_compilers.compile_knitout import compile_knitout
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout


class TestKnitout_Executer(TestCase):
    def test_test_and_organize_instructions(self):
        codes = parse_knitout("simple_course.k", pattern_is_file=True, debug_parser=False, debug_parser_layout=False)
        executor = Knitout_Executer(codes, Knitting_Machine())
        executor.write_executed_instructions("simple_course_executed.k")

    def test_compile(self):
        compile_knitout("simple_course_executed.k", "simple_course_executed.dat")
