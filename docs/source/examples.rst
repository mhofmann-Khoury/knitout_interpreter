Examples
========

📖 Usage Examples
------------------

Example 1: Parse Basic Stockinette
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout

    knitout_code = """
    ;!knitout-2
    ;;Machine: SWG091N2
    ;;Gauge: 15
    ;;Yarn-5: 50-50 Rust
    ;;Carriers: 1 2 3 4 5 6 7 8 9 10
    ;;Position: Right
    inhook 1;
    tuck + f1 1;
    tuck + f2 1;
    tuck + f3 1;
    tuck + f4 1;
    knit - f4 1
    knit - f3 1
    knit - f2 1
    knit - f1 1
    knit + f1 1;
    knit + f2 1;
    knit + f3 1;
    knit + f4 1;
    knit - f4 1
    knit - f3 1
    knit - f2 1
    knit - f1 1
    releasehook 1;
    outhook 1;
    """

    instructions = parse_knitout(knitout_code)
    # Process instructions...

Example 2: Pattern Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from knitout_interpreter.knitout_execution import Knitout_Executer

    # Analyze with executer
    executer = Knitout_Executer("complex_pattern.knitout")

    # Print analysis
    print("=== Pattern Analysis ===")
    print(f"Total instructions: {len(instructions)}")
    print(f"Execution time: {executer.execution_time} passes")
    print(f"Width: {executer.right_most_position - executer.left_most_position + 1} needles")

    # Analyze carriage passes
    for i, cp in enumerate(executer.carriage_passes):
        print(f"Pass {i+1}: {cp}")

Example 3: Working with Carriage Passes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from knitout_interpreter.knitout_execution import Knitout_Executer
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

    executer = Knitout_Executer(
        instructions
        knitting_machine=Knitting_Machine(),
        accepted_error_types=[],  # Optional: Knitting Machine Errors to ignore
        knitout_version=2
    )

    for carriage_pass in executer.carriage_passes:
        print(f"Pass direction: {carriage_pass.direction}")
        print(f"Instructions: {len(carriage_pass)}")
        print(f"Needle range: {carriage_pass.carriage_pass_range()}")
        print(f"Carriers used: {carriage_pass.carrier_set}")

Example 4: Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from knitout_interpreter.run_knitout import run_knitout
    from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Error

    try:
        instructions, machine, graph = run_knitout("pattern_with_errors.k")
        print("Pattern executed successfully!")
    except Knitout_Error as e:
        print(f"Knitting error occurred: {e}")
    except FileNotFoundError:
        print("Knitout file not found!")
