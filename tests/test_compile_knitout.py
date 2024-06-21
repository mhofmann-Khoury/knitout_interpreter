from unittest import TestCase

from knitout_interpreter.knitout_compilers.compile_knitout import compile_knitout
from knitout_interpreter.run_knitout import interpret_knitout


class Test(TestCase):
    def test_compile_knitout(self):
        compile_knitout("tube.k", "tube.dat")

    def test_interpret_knitout(self):
        interpret_knitout('rib.k', 'rib.dat')
