"""Module containing the debug_knitout decorator and associated typing verification."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Concatenate, ParamSpec, TypeVar

from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line

if TYPE_CHECKING:
    from knitout_interpreter.knitout_execution import Knitout_Executer

# Type variables for the decorator
PI = ParamSpec("PI")  # Captures all parameters for methods that start with the instruction
RI = TypeVar("RI")  # Captures return type for methods that start with the instruction


def debug_knitout_instruction(
    execution_method: Callable[Concatenate[Knitout_Executer, Knitout_Instruction | Knitout_Comment_Line, PI], RI]
) -> Callable[Concatenate[Knitout_Executer, Knitout_Instruction | Knitout_Comment_Line, PI], RI]:
    """
    Decorates a method of the Knitout_Executer class that executes lines of knitout code so that the lines can be debugged in the standard Python Debugger.

    Args:
        execution_method (Callable[Concatenate[Knitout_Executer, Knitout_Instruction | Knitout_Comment_Line, PI], RI]):
            The Knitout_Executer method that executes a knitout instruction which may be debugged.

    Returns:
        Callable[Concatenate[Knitout_Executer, Knitout_Instruction | Knitout_Comment_Line, PI], RI]:
            The execution method, wrapped with code to activate the Knitout_Debugger associated with the Knitout_Executer

    """

    @wraps(execution_method)
    def wrap_with_knitout_debug(self: Knitout_Executer, instruction: Knitout_Instruction | Knitout_Comment_Line, *args: PI.args, **kwargs: PI.kwargs) -> RI:
        """
        Args:
            self (Knitout_Executer): The Knitout_Executer object calling the wrapped method.
            instruction (Knitout_Instruction | Knitout_Comment_Line): The instruction being executed which may pause the debugger.
            *args: Any additional positional arguments passed to the wrapped method.
            **kwargs: Additional keyword arguments passed to the wrapped method.

        Returns:
            tuple[bool, bool, Knitout_Instruction | Knitout_Comment_Line]:
                A tuple containing the following information about the state of the machine based on this execution:
                * A boolean that indicates if the given instruction had an effect on the machine state.
                * A boolean indicating if the given instruction ended a carriage pass.
                * The instruction that was executed or a No-Op instruction that it was converted to if it had no effect on the process.

        Raises:
            Knitout_Machine_StateError: Any machine state errors caught in the process o executing the knitout.
        """
        if self.debugger is None:
            return execution_method(self, instruction, *args, **kwargs)

        self.debugger.debug_instruction(instruction)  # Handles pausing logic for knitout debugger
        try:
            return execution_method(self, instruction, *args, **kwargs)
        except Knitout_Machine_StateError as e:
            self.debugger.debug_exception(instruction, e)
            raise e

    return wrap_with_knitout_debug


PC = ParamSpec("PC")  # Captures all parameters for methods that handle a carriage pass
RC = TypeVar("RC")  # Captures return type for methods that handle a carriage pass


def debug_knitout_carriage_pass(execution_method: Callable[Concatenate[Knitout_Executer, PC], RC]) -> Callable[Concatenate[Knitout_Executer, PC], RC]:
    """
    Decorates a method of the Knitout_Executer class that executes the current carriage pass so that the lines can be debugged in the standard Python Debugger.

    Args:
        execution_method (Callable[Concatenate[Knitout_Executer, PC], RC]):
            The Knitout_Executer method that executes a knitout instruction which may be debugged.

    Returns:
        Callable[Concatenate[Knitout_Executer, Knitout_Instruction | Knitout_Comment_Line, PC], RC]:
            The execution method, wrapped with code to activate the Knitout_Debugger associated with the Knitout_Executer

    """

    @wraps(execution_method)
    def wrap_with_carriage_pass_debug(self: Knitout_Executer, *args: PC.args, **kwargs: PC.kwargs) -> RC:
        """

        Args:
            self (Knitout_Executer): The Knitout_Executer object calling the wrapped method.
            *args: Any additional positional arguments passed to the wrapped method.
            **kwargs: Additional keyword arguments passed to the wrapped method.

        Returns: The value of the wrapped method.

        Raises:
            Knitout_Machine_StateError: Any machine state errors caught in the process o executing the knitout.
        """
        if self.debugger is None:
            return execution_method(self, *args, **kwargs)

        self.debugger.debug_current_carriage_pass()  # Handles pausing logic for knitout debugger
        try:
            return execution_method(self, *args, **kwargs)
        except Knitout_Machine_StateError as e:
            self.debugger.debug_exception(self.executed_program[-1], e)
            raise e

    return wrap_with_carriage_pass_debug
