knitout-interpreter Documentation
==================================

.. image:: https://img.shields.io/pypi/v/knitout-interpreter.svg
   :target: https://pypi.org/project/knitout-interpreter
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/knitout-interpreter.svg
   :target: https://pypi.org/project/knitout-interpreter
   :alt: Python Versions

A comprehensive Python library for interpreting and executing knitout files used to control automatic V-Bed knitting machines. This library provides full support for the `Knitout specification <https://textiles-lab.github.io/knitout/knitout.html>`_ created by McCann et al.

Quick Start
-----------

Installation::

   pip install knitout-interpreter

Basic usage:

.. code-block:: python

   from knitout_interpreter import run_knitout

   # Parse and execute a knitout file
   instructions, machine, graph = run_knitout("pattern.k")
   print(f"Executed {len(instructions)} instructions")

Advanced usage:

.. code-block:: python

   from knitout_interpreter import Knitout_Executer
   from knitout_interpreter.knitout_language import parse_knitout
   from virtual_knitting_machine import Knitting_Machine

   # Parse knitout file
   instructions = parse_knitout("pattern.k", pattern_is_file=True)

   # Execute with analysis
   executer = Knitout_Executer(instructions, Knitting_Machine())
   print(f"Execution time: {executer.execution_time} carriage passes")
   print(f"Width required: {executer.left_most_position} to {executer.right_most_position}")

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/modules



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
