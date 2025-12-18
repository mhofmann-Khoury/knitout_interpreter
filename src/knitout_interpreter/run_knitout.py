"""A Module containing the run_knitout function for running a knitout file through the knitout interpreter."""

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.debugger.knitout_debugger import Knitout_Debugger
from knitout_interpreter.knitout_execution import execute_knitout
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


def run_knitout(knitout_file_name: str, debugger: Knitout_Debugger | None = None) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
    """Execute knitout instructions from a given file.

    This function provides a convenient interface for processing a knitout file
    through the knitout interpreter, returning the executed instructions and
    resulting machine state and knit graph.

    Args:
        knitout_file_name (str): Path to the file that contains knitout instructions.
        debugger (Knitout_Debugger, optional): An optional debugger to attach to the knitout process. Defaults to no debugger.

    Returns:
        tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
            A 3-element tuple containing the executed instructions, final machine state, and knit graph.
            * A list of Knitout_Line objects representing all processed instructions.
            * A Knitting_Machine object containing the final state of the virtual knitting machine after execution.
            * A Knit_Graph object representing the resulting fabric structure formed by the knitting operations.


    """
    return execute_knitout(knitout_file_name, debugger=debugger)
