"""A Module containing the run_knitout function for running a knitout file through the knitout interpreter."""
from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_language.Knitout_Context import Knitout_Context
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


def run_knitout(knitout_file_name: str) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
    """Execute knitout instructions from a given file.

    This function provides a convenient interface for processing a knitout file
    through the knitout interpreter, returning the executed instructions and
    resulting machine state and knit graph.

    Args:
        knitout_file_name: Path to the file that contains knitout instructions.

    Returns:
        A tuple containing:
            - List of executed knitout lines
            - Knitting machine state after execution
            - Knit graph formed by execution
    """
    context = Knitout_Context()
    return context.process_knitout_file(knitout_file_name)
