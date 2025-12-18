Debugging Knitout
=================

Knitout now supports debugging by attaching to the python debugger in whichever environment you are running it in.

Attaching a Debugger
--------------------

If you want to debug knitout code directly you need to attach a Knitout_Debugger to your Knitout_Executer.

You can attach a debugger at initialization of the Knitout_Executer or later in the process by calling executer.attach_debugger().

You can attach a debugger to a run_knitout process by filling the optional debugger parameter.

.. code-block:: python

    from knitout_interpreter.knitout_debugger.knitout_debugger import Knitout_Debugger
    from knitout_interpreter.run_knitout import run_knitout

    debugger = Knitout_Debugger()
    debugger.step()
    executer = run_knitout("debugged_knitout.k", debugger=debugger)
    executer.write_executed_instructions("executed_knitout.k")

To access the debugger, run your code in your standard python debugger (i.e., PDB from command line or the debugger in your IDE).
When a line of knitout is reached that triggers a debugging pause, it will pause your python debugger and reveal useful variables about the state of the knitting program.

From your debugging console you can live-update your debugger process by calling methods of the knitout_debugger variable. A helpful guide of instructions will be printed out to the debug console along with information about the context you paused in.

Setting BreakPoints
-------------------

You can set breakpoints for your debugger from your python code, in the debugging console, and directly in your knitout.

- The debugger will break on any Pause instructions in your knitout.

  - Additionally, you can set ";BreakPoint" comments in your knitout to break without a Pause instruction.

- To enable a breakpoint from python code call debugger.enable_breakpoint(N) with the line number you want to break on.

  .. code-block:: python

      debugger.enable_breakpoint(10)  # Debugger will pause on line 10 in your knitout file.

- You can disable any breakpoint that was set by python code by calling disable_breakpoint(N).

  .. code-block:: python

      debugger.disable_breakpoint(10)  # Debugger will not pause on line 10.


Controlling the Debugger's Flow
--------------------------------

The debugger has three modes:

- **Step**: Steps and pauses before every line of knitout.

  .. code-block:: python

      debugger.step()  # Debugger will pause before every instruction

- **Step-Carriage-Pass**: Steps and pauses before the beginning of every carriage pass.

  .. code-block:: python

      debugger.step_carriage_pass()  # Debugger will pause before every new carriage pass.

- **Continue**: Continues until a breakpoint is reached.

  .. code-block:: python

      debugger.continue_knitout()  # Debugger continue until an error or the end of the knitout program

You can check the current status of the debugger and determine its current mode by calling debugger.status().

Regardless of the flow, the debugger will pause right after an error is raised by the knitout process. This can help with determining the cause of the error.

You can modify the Step and Step-Carriage-Pass flow by applying conditions for pausing that must be met. A brief library of useful pausing conditions are available in knitout_interpreter.knitout_debugger.common_debugging_conditions module.

For example:

- You can pause only on instructions, stepping over all comments:

  .. code-block:: python

      from knitout_interpreter.knitout_debugger.common_debugging_conditions import not_comment

      debugger.enable_step_condition("Skip Comments", not_comment)

- You can pause on every transfer carriage pass:

  .. code-block:: python

      from knitout_interpreter.knitout_debugger.common_debugging_conditions import is_instruction_type
      from knitout_interpreter.knitout_operations.needle_instructions import Xfer_Instruction

      debugger.enable_step_condition("Hit Xfers", lambda d, i: is_instruction_type(d, i, Xfer_Instruction))


Machine Snapshots
-----------------

If you want to review the state of the knitting machine at the times the debugger paused, you can enable snapshots (on by default). Snapshots are a useful way of tracking the state of the knitting machine as it changes over time.

To enable snapshots:

.. code-block:: python

    debugger.enable_snapshots()


To disable snapshots:

.. code-block:: python

    debugger.disable_snapshots()

Taken snapshots can be accessed from the machine_snapshots variable which maps line numbers to the snapshot taken at that time:

.. code-block:: python

    snapshot_1 = debugger.machine_snapshots[1]
