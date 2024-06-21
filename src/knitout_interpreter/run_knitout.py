"""A Module containing the run_knitout function for running a knitout file through the knitout interpreter."""
from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_compilers.compile_knitout import Knitout_to_Machine_Compiler, compile_knitout
from knitout_interpreter.knitout_language.Knitout_Context import Knitout_Context
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


def run_knitout(knitout_file_name: str) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
    """
    Executes knitout in given file
    :param knitout_file_name: name of file that contains knitout
    :return: Knitting machine state after execution. Knit Graph formed by execution.
    """
    context = Knitout_Context()
    return context.process_knitout_file(knitout_file_name)


def interpret_knitout(knitout_file_name: str, output_file_name: str | None = None, compiler: Knitout_to_Machine_Compiler | None = None) -> bool:
    """
    :param knitout_file_name: The name of the knitout file to process.
    :param output_file_name: The name of the output file to create.
        DAT files for Shima Seiki.
    :param compiler: The compiler type to use.
    Defaults to Shima Seiki DAT compiler.
    :return: True, if the interpreter successfully processed the knitout into output instructions.
    False otherwise.
    """
    context = Knitout_Context()
    context.process_knitout_file(knitout_file_name)
    return compile_knitout(knitout_file_name, output_file_name, compiler)
