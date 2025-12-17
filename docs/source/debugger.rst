Debugging Knitout
=================

Knitout now supports debugging by attaching to the python debugger in whichever environment you are running it in.

Attaching a Debugger
--------------------

If you want to debug knitout code directly you need to attach a Knitout_Debbuger to your Knitout_Executer.

You can attach a debugger at initialization of the Knitout_Executer or later in the process by calling executer.attach_debugger().

.. code-block:: python

	from knitout_interpreter.knitout_debugger.knitout_debugger import Knitout_Debugger
	from knitout_interpreter.knitout_execution import Knitout_Executer
	from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout

	debugger = Knitout_Debugger()
    debugger.step()
    codes = parse_knitout(load_test_resource("debugged_knitout.k"), pattern_is_file=True)
    executer = Knitout_Executer(codes, debugger=debugger)
    executer.write_executed_instructions("executed_knitout.k")

Setting BreakPoints
--------------------
You can set breakpoints for you debugger from your python code, in the debugging console, and directly in your knitout.

- The debugger will break on any Pause instructions in your knitout.
	- Additionally, you can set ";BreakPoint" comments in your knitout to break without a Pause instruction.
- To set a breakpoint from python code call debugger.set_breakpoint(N) with the line number you want to break on.
	- Additionally, you can set a condition for breaking using this method. Simply provide an optional condition function when setting the breakpoint.
- You can clear a breakpoint that was set by python code by calling clear_breakpoint(N).

Additionally, you can temporarily hide breakpoints (keeping their conditions but ignoring them for a little while). This uses the methods:
- enable_breakpoint(N) which enables or creates a enw breakpoint at line N
- disable_breakpoint(N) which temporarily hides any breakpoint at line N
-

Controlling the Debugger's Flow
-------------------------------

The debugger has three modes:
- Step: Steps and pauses before every line of knitout.
- Step-Carriage-Pass: Steps and pauses before the beginning of every carriage pass.
- Continue: Continues untill a breakpoint is reached.

You can check the current status of the debugger and determine its current mode by calling debugger.status().

Regardless of the flow, the debugger will pause right after an execption is raised by the knitout process. This can help with determining the cause of the error.

Machine Snapshots
-----------------
If you want to review the state of the knitting machine at the times the debugger paused, you can enable snapshots (on by default). Snapshots are a useful way of tracking the state of the knitting machine as it changes over time.
