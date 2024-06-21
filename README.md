
# knitout_interpreter

[![PyPI - Version](https://img.shields.io/pypi/v/knitout-interpreter.svg)](https://pypi.org/project/knitout-interpreter)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/knitout-interpreter.svg)](https://pypi.org/project/knitout-interpreter)

-----
## Description
Support for interpreting knitout files used for controlling automatic V-Bed Knitting machines. This complies with the [Knitout specification](https://textiles-lab.github.io/knitout/knitout.html) created by McCann et al. 

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Run Knitout](#run-knitout)
  - [Knitout Executer](#knitout-executer)
- [License](#license)

## Installation

```console
pip install knitout-interpreter
```

## Usage

### Run Knitout
To execute a knitout file (e.g., "example.k") on a virtual knitting machine, you can use the run_knitout function from the [run_knitout Module](https://github.com/mhofmann-Khoury/knitout_interpreter/blob/main/src/knitout_interpreter/run_knitout.py). 
This will return a list of knitout-line objects in the order of execution,
the virtual knitting machine created and after the knitout operations have completed, and the knitgraph that is rendered by these knitout operations.

```python

from knitout_interpreter.run_knitout import run_knitout

knitout_lines, knitting_machine_state, knitted_knit_graph = run_knitout("example.k")
```

In addition to processing the knitout instructions into a list of instructions that executed on a virtual machine, this package supports interoperation with existing knitout compilers to Shima Seiki DAT files and Kniterate files. 

To interpret and convert the knitout code to a DAT file, execute the following:
```python
from knitout_interpreter.run_knitout import interpret_knitout
success= interpret_knitout("sample.k", "sample.dat")
```

The resulting DAT files can be viewed using the [Dat Viewer Interface from the CMU Textiles Lab](https://github.com/mhofmann-Khoury/knitout_interpreter/tree/main/src/knitout_interpreter/knitout_compilers/dat-viewer.html).

To generate Kniterate KCODE using the  [CMU Textiles Lab Kniterate compiler](https://github.com/textiles-lab/knitout-backend-kniterate), modify the code as follows.
```python
from knitout_interpreter.run_knitout import interpret_knitout
from knitout_interpreter.knitout_compilers.compile_knitout import Knitout_to_Machine_Compiler
success= interpret_knitout("sample.k", "sample.dat", Knitout_to_Machine_Compiler.Kniterate_Compiler)
```
### Knitout Executer

The [Knitout Execute Class](https://github.com/mhofmann-Khoury/knitout_interpreter/blob/main/src/knitout_interpreter/knitout_execution.py) provides additional support for analyzing an executed knitout program. 

It provides the following functionality:
- Determining the execution time of a knitout program measured in carriage passes (not lines of knitout).
- Finding the left and right most needle indices that are used during execution. This can be used to determine the width needed on a knitting machine.
- Testing the knitout instructions against common knitting errors
- Reorganizing a knitout program into carriage passes (such as sorting xfers to be in carriage pass order) and writing these out to a new file. 

## License

`knitout-interpreter` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.