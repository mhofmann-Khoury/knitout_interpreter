"""
knitout_operations: Individual knitout instruction implementations.

This module contains all the instruction classes that represent individual knitoutoperations.
These classes implement the complete Knitout specification v2, providing Python objects for every type of instruction that can appear in a knitout file.

The instructions are organized into several categories based on their function:

Needle Operations:
    Instructions that operate on specific needles to manipulate loops and yarn.
    These form the core knitting operations and directly affect the fabric structure.

Carrier Operations:
    Instructions that manage yarn carriers - the system that supplies yarn to the knitting needles.
    These control yarn insertion and removal.

Machine Control:
    Instructions that control machine state, including bed alignment (racking), execution pauses, and other machine-level operations.

Header Declarations:
    Special instructions that appear at the beginning of knitout files to specify machine configuration, yarn properties, and other setup parameters.

Base Classes:
    Fundamental classes that provide common functionality and type definitions for all instruction types.

Instruction Execution Model:
    Each instruction class implements an execute() method that applies the instruction's effects to a virtual knitting machine state.
    This allows for simulation, validation, and analysis of knitout programs before running them on physical machines.

Example:
    Working with specific instruction types:

    >>> from knitout_interpreter.knitout_operations import Knit_Instruction, In_Instruction
    >>> from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    >>> from virtual_knitting_machine.machine_components.needles.Needle import Needle
    >>> from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set
    >>>
    >>> # Create machine and components
    >>> machine = Knitting_Machine()
    >>> needle = Needle(is_front=True, position=5)
    >>> carriers = Yarn_Carrier_Set([1])
    >>>
    >>> # Create and execute instructions
    >>> in_instruction = In_Instruction(1)
    >>> knit_instruction = Knit_Instruction(needle, "rightward", carriers)
    >>>
    >>> in_instruction.execute(machine)
    >>> knit_instruction.execute(machine)

    Working with header declarations:

    >>> from knitout_interpreter.knitout_operations import Machine_Header_Line, Gauge_Header_Line
    >>>
    >>> machine_header = Machine_Header_Line("SWG091N2")
    >>> gauge_header = Gauge_Header_Line(15)
    >>>
    >>> # Headers can update machine configuration
    >>> machine_header.execute(machine)
    >>> gauge_header.execute(machine)

    Instruction type checking and properties:

    >>> from knitout_interpreter.knitout_operations import Knitout_Instruction_Type
    >>>
    >>> instruction_type = Knitout_Instruction_Type.Knit
    >>> print(f"Requires carrier: {instruction_type.requires_carrier}")
    >>> print(f"Is needle instruction: {instruction_type.is_needle_instruction}")
    >>> print(f"Compatible with tuck: {instruction_type.compatible_pass(Knitout_Instruction_Type.Tuck)}")
"""

# Import needle operations - core knitting instructions
from .needle_instructions import (
    # Loop-making instructions
    Knit_Instruction,  # Create new loops, dropping old ones
    Tuck_Instruction,  # Create new loops, keeping old ones
    Split_Instruction,  # Split loops between two needles

    # Loop manipulation instructions
    Drop_Instruction,  # Remove loops from needles
    Xfer_Instruction,  # Transfer loops between needles
    Miss_Instruction,  # Position carriers without forming loops

    # Base classes
    Needle_Instruction,  # Base class for all needle operations
    Loop_Making_Instruction,  # Base class for loop-creating operations
)

# Import carrier operations - yarn management
from .carrier_instructions import (
    # Basic carrier movement
    In_Instruction,  # Bring carrier into knitting area
    Out_Instruction,  # Move carrier out of knitting area

    # Hook-based carrier operations
    Inhook_Instruction,  # Hook carrier into position
    Outhook_Instruction,  # Hook carrier out of position
    Releasehook_Instruction,  # Release hooked carrier
)

# Import machine control operations
from .Rack_Instruction import Rack_Instruction  # Set bed alignment
from .Pause_Instruction import Pause_Instruction  # Pause machine execution

# Import specialized instructions
from .kick_instruction import Kick_Instruction  # Kickback positioning

# Import header declarations - machine configuration
from .Header_Line import (
    # Specific header types
    Machine_Header_Line,  # Specify machine type
    Gauge_Header_Line,  # Set machine gauge
    Yarn_Header_Line,  # Define yarn properties
    Carriers_Header_Line,  # Configure available carriers
    Position_Header_Line,  # Set knitting position

    # Base classes and utilities
    Knitout_Header_Line_Type,  # Enumeration of header types
    Knitting_Machine_Header,  # Header management utility
    get_machine_header,  # Utility function
)

# Import base instruction classes and types
from .knitout_instruction import (
    Knitout_Instruction_Type,  # Enumeration of instruction types
)

# Import base line classes
from .Knitout_Line import (
    Knitout_Comment_Line,  # Comment lines
    Knitout_Version_Line,  # Version specification lines
)

# Define the public API - organized by functional categories
__all__ = [
    # ===== NEEDLE OPERATIONS =====
    # Primary knitting instructions
    "Knit_Instruction",
    "Tuck_Instruction",
    "Split_Instruction",

    # Loop manipulation
    "Drop_Instruction",
    "Xfer_Instruction",
    "Miss_Instruction",

    # Specialized needle operations
    "Kick_Instruction",

    # ===== CARRIER OPERATIONS =====
    # Basic carrier movement
    "In_Instruction",
    "Out_Instruction",

    # Hook-based operations
    "Inhook_Instruction",
    "Outhook_Instruction",
    "Releasehook_Instruction",

    # ===== MACHINE CONTROL =====
    "Rack_Instruction",
    "Pause_Instruction",

    # ===== HEADER DECLARATIONS =====
    # Specific header types
    "Machine_Header_Line",
    "Gauge_Header_Line",
    "Yarn_Header_Line",
    "Carriers_Header_Line",
    "Position_Header_Line",

    # Header utilities
    "Knitout_Header_Line_Type",
    "Knitting_Machine_Header",
    "get_machine_header",

    # ===== BASE CLASSES AND TYPES =====
    # Instruction framework
    "Knitout_Instruction_Type",

    # Line framework
    "Knitout_Comment_Line",
    "Knitout_Version_Line",
]

# Extended documentation for module organization
__doc__ += """

Module Organization:
    needle_instructions.py: All needle-based operations (knit, tuck, xfer, etc.)
    carrier_instructions.py: Yarn carrier management operations
    Header_Line.py: Machine configuration and setup declarations
    Rack_Instruction.py: Bed alignment control
    Pause_Instruction.py: Execution pause control
    kick_instruction.py: Specialized kickback positioning
    knitout_instruction.py: Base classes and instruction type definitions
    Knitout_Line.py: Base classes for all knitout file lines

Instruction Hierarchy:
    Knitout_Line (base for all knitout file content)
    ├── Knitout_Instruction (base for executable instructions)
    │   ├── Needle_Instruction (needle-based operations)
    │   │   ├── Loop_Making_Instruction (creates loops)
    │   │   │   ├── Knit_Instruction
    │   │   │   ├── Tuck_Instruction
    │   │   │   └── Split_Instruction
    │   │   ├── Drop_Instruction
    │   │   ├── Xfer_Instruction
    │   │   ├── Miss_Instruction
    │   │   │  └── Kick_Instruction
    │   ├── Yarn_Carrier_Instruction (carrier operations)
    │   │   ├── In_Instruction / Out_Instruction
    │   │   └── Hook_Instruction
    │   │       ├── Inhook_Instruction / Outhook_Instruction
    │   │       └── Releasehook_Instruction
    │   ├── Rack_Instruction
    │   └── Pause_Instruction
    ├── Knitout_Header_Line (configuration declarations)
    │   ├── Machine_Header_Line
    │   ├── Gauge_Header_Line
    │   ├── Yarn_Header_Line
    │   ├── Carriers_Header_Line
    │   └── Position_Header_Line
    ├── Knitout_Comment_Line
    └── Knitout_Version_Line

Usage Patterns:
    Import specific instruction types:
        from knitout_interpreter.knitout_operations import Knit_Instruction, Tuck_Instruction

    Import base classes for extension:
        from knitout_interpreter.knitout_operations import Knitout_Instruction, Needle_Instruction
"""
