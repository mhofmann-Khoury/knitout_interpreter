"""Base class for Knitout Lines of code"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, ParamSpec, TypeVar

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError

P = ParamSpec("P")
R = TypeVar("R")


def capture_execution_context(func: Callable[Concatenate[Knitout_Line, P], R]) -> Callable[Concatenate[Knitout_Line, P], R]:
    """
    Decorator that adds execution context to exceptions raised during execution of knitout lines.

    Args:
        func: Function to be decorated (method taking self as first parameter).

    Returns:
        The decorated function with the same signature.
    """

    @wraps(func)
    def _exception_context_update_wrapper(self: Knitout_Line, *args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            raise Knitout_Machine_StateError(self, e) from e

    return _exception_context_update_wrapper


class Knitout_Line:
    """General class for lines of knitout.

    Attributes:
        comment (str | None): The comment that follows the knitout instruction. None if there is no comment.
        original_line_number (int | None): The line number of this instruction in its original file or None if that is unknown.
    """

    _Lines_Made = 0

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically wrap execute() method in all subclasses."""
        super().__init_subclass__(**kwargs)

        # Check if this class defines its own execute method
        if "execute" in cls.__dict__:
            # Wrap it with the decorator using setattr
            original_execute = cls.execute
            cls.execute = capture_execution_context(original_execute)  # type: ignore[method-assign]

    def __init__(self, comment: str | None = None, interrupts_carriage_pass: bool = False) -> None:
        """
        Args:
            comment (str, optional): The comment following this instruction. Defaults to no comment.
            interrupts_carriage_pass (bool, optional): True if this type of instruction interrupts a carriage pass. Defaults to False.
        """
        Knitout_Line._Lines_Made += 1
        self._creation_time: int = Knitout_Line._Lines_Made
        self.comment: str | None = comment
        self.original_line_number: int | None = None
        self._follow_comments: list[Knitout_Comment_Line] = []
        self._interrupts_carriage_pass: bool = interrupts_carriage_pass

    @property
    def interrupts_carriage_pass(self) -> bool:
        """Check if this line interrupts a carriage pass.

        Returns:
            bool: True if this type of line interrupts a carriage pass. False if it is only used for comments or setting information.
        """
        return self._interrupts_carriage_pass

    @property
    def follow_comments(self) -> list[Knitout_Comment_Line]:
        """
        Returns:
            list[Knitout_Comment_Line]: A list of Knitout_Comment_Line objects that follow this line.
        """
        return self._follow_comments

    @property
    def has_comment(self) -> bool:
        """Check if this line has a comment.

        Returns:
            bool: True if comment is present. False, otherwise.
        """
        return self.comment is not None

    @property
    def comment_str(self) -> str:
        """Get the comment as a formatted string.

        Returns:
            The comment formatted as a string with appropriate formatting.
        """
        if not self.has_comment:
            return "\n"
        else:
            return f";{self.comment}\n"

    @capture_execution_context
    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Execute the instruction on the machine state.

        Args:
            machine_state (Knitting_Machine): The knitting machine state to update.

        Returns:
            bool: True if the process completes an update. False, otherwise.
        """
        return False

    def __str__(self) -> str:
        return self.comment_str

    @property
    def injected(self) -> bool:
        """Check if instruction was marked as injected.

        Returns:
            True if instruction was marked as injected by a negative line number.
        """
        return self.original_line_number is not None and self.original_line_number < 0

    def id_str(self) -> str:
        """Get string representation with original line number if present.

        Returns:
            str: String with original line number added if present.
        """
        if self.original_line_number is not None:
            return f"{self.original_line_number}:{self}"[:-1]
        else:
            return str(self)[-1:]

    def __repr__(self) -> str:
        if self.original_line_number is not None:
            return self.id_str()
        else:
            return str(self)

    def __lt__(self, other: Knitout_Line) -> bool:
        """
        Args:
            other (Knitout_Line): A Knitout_Line object to compare.

        Returns:
            bool:
                True if the original line number is less than that of the other knitout line.
                If original line numbers are not present, instructions without line numbers are less than those with line numbers.
        """
        if self.original_line_number is None:
            return other.original_line_number is not None
        elif other.original_line_number is None:
            return False
        else:
            return bool(self.original_line_number < other.original_line_number)

    def __hash__(self) -> int:
        """
        Returns:
            int: Unique integer based on the time that this instruction was created in the execution.
        """
        return hash(self._creation_time)


class Knitout_Comment_Line(Knitout_Line):
    """Represents a comment line in knitout."""

    def __init__(self, comment: None | str | Knitout_Line | Knitout_Comment_Line):
        """Initialize a comment line.

        Args:
            comment (None | str | Knitout_Line | Knitout_Comment_Line): The comment text, or a Knitout_Line to convert to a comment.
        """
        original_line_number = None
        if isinstance(comment, Knitout_Line):
            original_line_number = comment.original_line_number
            comment = str(Knitout_Comment_Line.comment_str) if isinstance(comment, Knitout_Comment_Line) else f"No-Op:\t{comment}".strip()
        super().__init__(comment, interrupts_carriage_pass=False)
        if original_line_number is not None:
            self.original_line_number = original_line_number

    def execute(self, machine_state: Knitting_Machine) -> bool:
        return True


class Knitout_No_Op(Knitout_Comment_Line):
    """Represents a comment line in knitout.

    Attributes:
        original_instruction (Knitout_Line): The original instruction that was commented out by this no-op.
    """

    NO_OP_TERM: str = "No-Op:"  # The term used to recognize no-op operations

    def __init__(self, no_op_operation: Knitout_Line, additional_comment: str | None = None):
        """Initialize a comment line.

        Args:
            no_op_operation (Knitout_Line): The operation with no effect on the machine state to convert to a no-op comment.
            additional_comment (str, optional): Additional details to include with the no-op. Defaults to no additional details.
        """
        comment = str(Knitout_Comment_Line.comment_str) if isinstance(no_op_operation, Knitout_Comment_Line) else f"{self.NO_OP_TERM} {no_op_operation}".strip()
        if additional_comment is not None:
            comment = f"{comment}; {additional_comment}"
        self.original_instruction: Knitout_Line = no_op_operation
        super().__init__(comment)
        self.original_line_number = no_op_operation.original_line_number

    def execute(self, machine_state: Knitting_Machine) -> bool:
        return False  # No-Ops do not need to be included in executed knitout code.


class Knitout_BreakPoint(Knitout_Comment_Line):
    BP_TERM: str = "BreakPoint"

    def __init__(self, additional_comment: str | None = None):
        self.bp_comment: str | None = additional_comment
        super().__init__(f"{self.BP_TERM}: {additional_comment}")
