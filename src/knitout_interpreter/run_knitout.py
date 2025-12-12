"""A Module containing the run_knitout function for running a knitout file through the knitout interpreter."""

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_language.Knitout_Context import Knitout_Context
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction


def run_knitout(knitout_file_name: str) -> tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
    """Execute knitout instructions from a given file.

    This function provides a convenient interface for processing a knitout file
    through the knitout interpreter, returning the executed instructions and
    resulting machine state and knit graph.

    Args:
        knitout_file_name (str): Path to the file that contains knitout instructions.

    Returns:
        tuple[list[Knitout_Instruction], Knitting_Machine, Knit_Graph]:
            A 3-element tuple containing the executed instructions, final machine state, and knit graph.
            * A list of Knitout_Line objects representing all processed instructions.
            * A Knitting_Machine object containing the final state of the virtual knitting machine after execution.
            * A Knit_Graph object representing the resulting fabric structure formed by the knitting operations.

    Example:
        Basic usage:

        .. code-block:: python

            instructions, machine, graph = run_knitout("pattern.k")
            print(f"Executed {len(instructions)} instructions")
            print(f"Machine has {len(machine.needle_beds)} needle beds")
            print(f"Graph contains {graph.node_count} nodes")

    """
    context = Knitout_Context()
    lines, machine, graph = context.process_knitout_file(knitout_file_name)
    return lines, machine, graph
