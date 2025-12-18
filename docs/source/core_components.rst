Core Components
===============

📚 Main Components
------------------

Knitout Executer
~~~~~~~~~~~~~~~~

To analyse a knitout program beyond basic verification, access various kee attributes of the ``Knitout_Executer`` class.

**Key Properties:**

- ``execution_time``: Number of carriage passes that will be executed
- ``left_most_position`` / ``right_most_position``: The range of needle positions in the executed file
- ``carriage_passes``: List of carriage passes in the order they are executed
- ``resulting_knit_graph``: Final fabric structure
- ``machine_state``: The machine state at the end of the process.

Additionally, you can collect snapshots of the machine state at key moments in the execution. Initialize the executer with specific targets and add and remove targets during an execution process.

.. code-block:: python

	executer = Knitout_Executer('knitout.k', snapshot_targets = set(1)) # Will create a snapshot on line 1.
	executer.enable_snapshot(10) # adds a snapshot on line 10.

Instruction Types
~~~~~~~~~~~~~~~~~

The library supports all knitout operations as Python classes:

Needle Operations
^^^^^^^^^^^^^^^^^
- ``Knit_Instruction``: Create new loops, stitch through the old one
- ``Tuck_Instruction``: Create new loops, keeping old ones
- ``Split_Instruction``: Creates a loop on first specified needle while moving existing loops to the second specified needle
- ``Drop_Instruction``: Remove loops from needles
- ``Xfer_Instruction``: Transfer loops between needles
- ``Miss_Instruction``: Position carriers without forming loops
- ``Kick_Instruction``: Specialized miss for kickbacks

Carrier Operations
^^^^^^^^^^^^^^^^^^
- ``In_Instruction`` / ``Out_Instruction``: Move carriers in/out of knitting area
- ``Inhook_Instruction`` / ``Outhook_Instruction``: Move carriers in/out of knitting area using yarn-inserting hook
- ``Releasehook_Instruction``: Release carriers on the yarn-inserting hook

Machine Control
^^^^^^^^^^^^^^^
- ``Rack_Instruction``: Set bed alignment and all-needle mode
- ``Pause_Instruction``: Pause machine execution

Header Declarations
^^^^^^^^^^^^^^^^^^^
- ``Machine_Header_Line``: Specify machine type
- ``Gauge_Header_Line``: Set machine gauge
- ``Yarn_Header_Line``: Define yarn properties
- ``Carriers_Header_Line``: Configure available carriers
- ``Position_Header_Line``: Set knitting position
- ``Knitout_Version_Line``: Declares the version of the knitout file.

Helpful Comments
^^^^^^^^^^^^^^^^
- ``Knitout_Comment_Line``: A line with only comment information and no effect on execution.
- ``Knitout_No_Op``: A commented instruction created in the execution analysis process.
	- No-Ops are specified ";No-Op:..."
- ``Knitout_BreakPoint``: A way of setting a breakpoint directly from the knitout file.
	- Breakpoints are specified ";Breakpoint:..."

Carriage Pass Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~

The library automatically organizes instructions into carriage passes for efficient execution:

.. code-block:: python

    # Access carriage passes from the executer
    for pass_index, carriage_pass in enumerate(executer.carriage_passes):
        print(f"Pass {pass_index + 1}:")
        print(f"  Direction: {carriage_pass.direction}")
        print(f"  Instructions: {len(carriage_pass)}")
        print(f"  Needle range: {carriage_pass.carriage_pass_range()}")
        print(f"  Carriers used: {carriage_pass.carrier_set}")

**Carriage Pass Properties:**

- ``direction``: Left-to-right or right-to-left movement
- ``carriage_pass_range()``: Needle positions covered in this pass
- ``carrier_set``: Set of yarn carriers used in this pass
- ``len(carriage_pass)``: Number of instructions in this pass

Parser Components
~~~~~~~~~~~~~~~~~

Knitout Parser
^^^^^^^^^^^^^^

The parser converts knitout text files into structured Python objects:

.. code-block:: python

    from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout

    # Parse from file
    instructions = parse_knitout("pattern.k", pattern_is_file=True)

    # Parse from string
    knitout_string = """
    ;!knitout-2
    ;;Machine: SWG091N2
    knit + f1 1
    """
    instructions = parse_knitout(knitout_string, pattern_is_file=False)

**Parser Features:**

- Supports knitout specification v2
- Handles header declarations
- Validates instruction syntax
- Converts to structured Python objects
- Provides detailed error messages for invalid syntax

Virtual Machine Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration with Virtual Knitting Machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The library integrates seamlessly with the virtual-knitting-machine library:

.. code-block:: python

    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    from knitout_interpreter.run_knitout import run_knitout

    # The run_knitout function returns the final machine state
    instructions, final_machine, knit_graph = run_knitout("pattern.k")

    # Access machine properties
    print(f"Machine has {len(final_machine.needle_beds)} needle beds")
    print(f"Active needles: {final_machine.active_needle_count}")

**Machine State Tracking:**

- Loop positions and types
- Carrier positions and states
- Needle bed configurations
- Error detection and reporting
