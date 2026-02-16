from dataclasses import dataclass
from typing import TypeVar

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Specification import Knitting_Machine_Specification
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violation_policy import Knitting_Machine_Error_Policy

from knitout_interpreter.knitout_execution_structures.knitout_loops import Knitout_Loop

Knitout_LoopT = TypeVar("Knitout_LoopT", bound=Knitout_Loop)


@dataclass(frozen=True)
class Knitout_Machine_Specification(Knitting_Machine_Specification):
    """Subclass of Knitout_Machine_Specification that generates Knitout_Loops"""

    loop_class: type[Knitout_Loop] = Knitout_Loop


class Knitout_Knitting_Machine(Knitting_Machine[Knitout_LoopT]):

    def __init__(
        self,
        machine_specification: Knitout_Machine_Specification | None = None,
        knit_graph: Knit_Graph[Knitout_LoopT] | None = None,
        violation_policy: Knitting_Machine_Error_Policy | None = None,
    ) -> None:
        """Initialize a virtual knitting machine with specified configuration.

        Args:
            machine_specification (Knitout_Machine_Specification, optional): Configuration parameters for the machine. Defaults to Knitting_Machine_Specification().
            knit_graph (Knit_Graph | None, optional): Existing knit graph to use, creates new one if None. Defaults to None.
            violation_policy (Knitting_Machine_Error_Policy, optional): The error handling policy for the machine. Defaults to a policy which raises all errors.
        """
        if machine_specification is None:
            machine_specification = Knitout_Machine_Specification()
        super().__init__(machine_specification, knit_graph, violation_policy)
        self._machine_specification: Knitout_Machine_Specification = machine_specification

    @property
    def machine_specification(self) -> Knitout_Machine_Specification:
        """
        Returns:
            Knitout_Machine_Specification: The specification of this machine.
        """
        return self._machine_specification
