"""Module containing the debug_knitout decorator and associated typing verification."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar, cast

from knitout_interpreter.debugger.knitout_debugger import Debuggable_Knitout_Execution
from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line

# Type variables for the decorator
P = ParamSpec("P")  # Captures all parameters for methods that start with the instruction
R = TypeVar("R")  # Captures return type for methods that start with the instruction


def debug_knitout_instruction(execution_method: Callable[P, R]) -> Callable[P, R]:
    """
    Decorates a method of the Knitout_Executer class that executes lines of knitout code so that the lines can be debugged in the standard Python Debugger.

    Args:
        execution_method (Callable[[Knitout_Executer, Knitout_Instruction | Knitout_Comment_Line], None]):
            The Knitout_Executer method that executes a knitout instruction which may be debugged.

    Returns:
        Callable[[Knitout_Executer, Knitout_Instruction | Knitout_Comment_Line], None]:  The execution method, wrapped with code to activate the Knitout_Debugger associated with the Knitout_Executer
    """

    @wraps(execution_method)
    def wrap_with_knitout_debug(*_args: P.args, **_kwargs: P.kwargs) -> R:
        """
        Args:
            *_args:
                Positional arguments passed to the wrapped method. The positional argument expected are:
                - self (Knitout_Executer): The Knitout_Executer object calling the wrapped method.
                - instruction (Knitout_Instruction | Knitout_Comment_Line): The instruction being executed which may pause the debugger.
            **_kwargs: Additional keyword arguments passed to the wrapped method.
        """
        self: Debuggable_Knitout_Execution = cast(Debuggable_Knitout_Execution, _args[0] if len(_args) >= 1 else _kwargs["self"])
        instruction: Knitout_Instruction | Knitout_Comment_Line = cast(Knitout_Instruction | Knitout_Comment_Line, _args[1] if len(_args) >= 2 else _kwargs["instruction"])
        if self.debugger is None:
            return execution_method(*_args, **_kwargs)

        self.debugger.debug_instruction(instruction)  # Handles pausing logic for knitout debugger
        try:
            return execution_method(*_args, **_kwargs)
        except Knitout_Machine_StateError as e:
            self.debugger.debug_exception(instruction, e)
            raise

    return wrap_with_knitout_debug
