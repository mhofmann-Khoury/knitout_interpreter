
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
  - [Knitout Executer](#knitout-executer)
- [License](#license)

## Installation

```console
pip install knitout-interpreter
```

## Usage
### Knitout Executer

The [Knitout Execute Class](https://github.com/mhofmann-Khoury/knitout_interpreter/blob/main/src/knitout_interpreter/knitout_execution.py) provides additional support for analyzing an executed knitout program. 

It provides the following functionality:
- Determining the execution time of a knitout program measured in carriage passes (not lines of knitout).
- Finding the left and right most needle indices that are used during execution. This can be used to determine the width needed on a knitting machine.
- Testing the knitout instructions against common knitting errors
- Reorganizing a knitout program into carriage passes (such as sorting xfers to be in carriage pass order) and writing these out to a new file. 

## License

`knitout-interpreter` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.