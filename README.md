
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

### Knitout Executer

The [Knitout Execute Class](https://github.com/mhofmann-Khoury/knitout_interpreter/blob/main/src/knitout_interpreter/knitout_execution.py) provides additional support for analyzing an executed knitout program. 

It provides the following functionality:
- Determining the execution time of a knitout program measured in carriage passes (not lines of knitout).
- Finding the left and right most needle indices that are used during execution. This can be used to determine the width needed on a knitting machine.
- Testing the knitout instructions against common knitting errors
- Reorganizing a knitout program into carriage passes (such as sorting xfers to be in carriage pass order) and writing these out to a new file. 

## License

`knitout-interpreter` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.