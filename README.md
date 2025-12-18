# knitout-interpreter

[![PyPI - Version](https://img.shields.io/pypi/v/knitout-interpreter.svg)](https://pypi.org/project/knitout-interpreter)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/knitout-interpreter.svg)](https://pypi.org/project/knitout-interpreter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-github.io-blue)](https://mhofmann-khoury.github.io/knitout_interpreter/)

A Python library for interpreting, executing, and debugging [knitout](https://textiles-lab.github.io/knitout/knitout.html) files used to control automatic V-Bed knitting machines.

## Installation
```bash
pip install knitout-interpreter
```

## Quick Example
```python
from knitout_interpreter.run_knitout import run_knitout

# Execute a knitout file
instructions, machine, knit_graph = run_knitout("pattern.k")
```

## Documentation

**Full documentation:** [https://mhofmann-khoury.github.io/knitout_interpreter/](https://mhofmann-khoury.github.io/knitout_interpreter/)

## Links

- **PyPI**: https://pypi.org/project/knitout-interpreter
- **Documentation**: https://mhofmann-khoury.github.io/knitout_interpreter/
- **Source Code**: https://github.com/mhofmann-Khoury/knitout_interpreter
- **Issues**: https://github.com/mhofmann-Khoury/knitout_interpreter/issues

---

**Made by the Northeastern University ACT Lab**
