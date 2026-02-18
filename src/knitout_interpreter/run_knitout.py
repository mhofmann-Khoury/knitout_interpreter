"""A Module containing the run_knitout function for running a knitout file through the knitout interpreter."""

from collections.abc import Iterable

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import Violation

from knitout_interpreter.debugger.knitout_debugger import Knitout_Debugger
from knitout_interpreter.knitout_execution import execute_knitout
from knitout_interpreter.knitout_execution_structures.knitout_program import Knitout_Program


def run_knitout(knitout_file_name: str, debugger: Knitout_Debugger | None = None, relax_violations: bool | Iterable[Violation] = False) -> tuple[Knitout_Program, Knitting_Machine, Knit_Graph]:
    """Execute knitout instructions from a given file.

    This function provides a convenient interface for processing a knitout file through the knitout interpreter, returning the executed instructions and resulting machine state and knit graph.

    Args:
        knitout_file_name (str): Path to the file that contains knitout instructions.
        debugger (Knitout_Debugger, optional): An optional debugger to attach to the knitout process. Defaults to no debugger.
        relax_violations (bool | Iterable[Violation], optional): If True, all violations are relaxed. If violations are given, those violations are relaxed. Defaults to False (full validation).

    Returns:
        tuple[Knitout_Program, Knitting_Machine, Knit_Graph]:
            A 3-element tuple containing the executed instructions, final machine state, and knit graph.
            * A list of Knitout_Line objects representing all processed instructions.
            * A Knitting_Machine object containing the final state of the virtual knitting machine after execution.
            * A Knit_Graph object representing the resulting fabric structure formed by the knitting operations.


    """
    return execute_knitout(knitout_file_name, debugger=debugger, relax_violations=relax_violations)
