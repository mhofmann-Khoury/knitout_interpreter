"""
knitout_execution_structures: Data structures for organizing knitout execution.

This module provides specialized data structures that organize knitout instructions into meaningful execution units.
These structures bridge the gap between individual knitout instructions and the actual execution patterns on knitting machines.

Key Concepts:
    Carriage Pass: A sequence of instructions that can be executed in a single pass of the knitting machine carriage.
     Instructions in a carriage pass share common properties like direction, racking, and carrier usage.

    Organization: Instructions are automatically grouped into carriage passes based on machine constraints and execution efficiency.
    This organization is crucial for accurate timing analysis and machine operation.

Core Components:
    - Carriage_Pass: Main data structure representing a carriage pass
    - Pass organization and merging logic
    - Execution timing and analysis capabilities
    - Needle range and width calculations

Machine Execution Model:
    Real knitting machines operate in carriage passes rather than individual instructions.
    A carriage pass represents one sweep of the carriage across the needle bed, during which multiple operations can occur simultaneously.

    Pass Properties:
        - Direction: Leftward or rightward carriage movement
        - Racking: Bed alignment for the entire pass
        - Carriers: Yarn carriers active during the pass
        - Needle Range: Leftmost to rightmost needles involved

Example:
    Working with carriage passes from execution:

    >>> from knitout_interpreter.knitout_execution import Knitout_Executer
    >>> from knitout_interpreter.knitout_language.Knitout_Parser import  parse_knitout
    >>> from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
    >>> from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    >>>
    >>> instructions = parse_knitout('knit + f1 1')
    >>> executer = Knitout_Executer(instructions, Knitting_Machine())
    >>> for i, carriage_pass in enumerate(executer.carriage_passes):
    ...     print(f"Pass {i+1}: {carriage_pass}")

    Analyzing pass properties:

    >>> # Get timing and width information
    >>> execution_time = len(executer.carriage_passes)  # Number of passes
    >>> left, right = carriage_pass.carriage_pass_range()
    >>> width = right - left + 1
    >>> print(f"Passes over {width} needles from position {left} to {right}")

Pass Organization Rules:
    Instructions are grouped into carriage passes based on:
    - Execution direction (leftward/rightward)
    - Racking requirements (bed alignment)
    - Carrier usage (which yarns are active)
    - Instruction compatibility (can execute simultaneously)
    - Machine constraints (needle accessibility, timing)
"""

# Import the main execution structure
from .Carriage_Pass import Carriage_Pass

# Define what gets imported with "from knitout_execution_structures import *"
__all__ = [
    "Carriage_Pass",  # Main data structure for organizing execution
]

# Module documentation continues with technical details
__doc__ += """

Technical Implementation Details:
    Carriage_Pass.py: Main implementation of carriage pass data structure

    Pass Organization Algorithm:
        1. Instructions are processed sequentially
        2. Compatible instructions are grouped into the same pass
        3. Incompatible instructions start a new pass
        4. Passes are automatically ordered for machine execution

    Compatibility Rules:
        Instructions can share a carriage pass if they have:
        - Same execution direction
        - Same racking requirements
        - Same carrier usage
        - Compatible instruction types
        - Non-overlapping needle positions

Performance Considerations:
    - Pass organization is O(n) where n is the number of instructions
    - Memory usage scales with the number of unique carriage passes
"""
