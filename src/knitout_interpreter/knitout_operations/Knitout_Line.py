"""Base class for Knitout Lines of code"""

from __future__ import annotations

import copy
from collections.abc import Callable
from functools import wraps
from typing import Any, ClassVar, Concatenate, ParamSpec, Self, TypeVar, cast

from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_execution_structures.Knitout_Knitting_Machine import Knitout_Knitting_Machine

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
    """

    interrupts_carriage_pass: ClassVar[bool] = False  # If True, indicates that this type of knitout line will interrupt a carriage pass.

    def __new__(cls, *args: Any, **kwargs: Any) -> Knitout_Line:
        """
        Counts the number of knitout lines created while running a program. Ensures a unique identifier for each knitout line.
        """
        instance = super().__new__(cls)
        instance._creation_time = Knitout_Line._next_line()
        return instance

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically wrap execute() method in all subclasses."""
        super().__init_subclass__(**kwargs)

        # Check if this class defines its own execute method
        if "execute" in cls.__dict__:
            # Wrap it with the decorator using setattr
            original_execute = cls.execute
            cls.execute = capture_execution_context(original_execute)  # type: ignore[method-assign]

    def __init__(self, comment: str | None = None) -> None:
        """
        Args:
            comment (str, optional): The comment following this instruction. Defaults to no comment.
        """
        self._creation_time: int = self._next_line()
        self.comment: str | None = comment
        self._source_program: str | None = None
        self._original_line_number: int | None = None
        self._line_number: int | None = None
        self._follow_comments: list[Knitout_Comment_Line] = []

    @property
    def has_line_number(self) -> bool:
        """
        Returns:
            bool: True if the original line number of this knitout line has been set.
        """
        return self._original_line_number is not None

    @property
    def original_line_number(self) -> int:
        """
        Returns:
            int: The original position of this line from the program it was parsed from.
        """
        if self._original_line_number is None:
            raise AttributeError("Original Line number has not been set before being accessed.")
        return self._original_line_number

    @property
    def line_number(self) -> int:
        """
        Returns:
            int: The current position of the line in a program.
        """
        if self._line_number is None:
            raise AttributeError("Line number has not been set before being accessed.")
        return self._line_number

    @property
    def source_program(self) -> str | None:
        """
        Returns:
            str | None: The name of the program this was parsed from or None if that value is unknown.
        """
        return self._source_program

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
    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
        """Execute the instruction on the machine state.

        Args:
            machine_state (Knitting_Machine): The knitting machine state to update.

        Returns:
            bool: True if the process completes an update. False, otherwise.
        """
        return False

    def id_str(self) -> str:
        """Get string representation with original line number if present.

        Returns:
            str: String with original line number added if present.
        """
        if self._original_line_number is not None:
            return f"{self._original_line_number}:{self}"[:-1]
        else:
            return str(self)[-1:]

    def set_line(self, line_number: int, source: str | None = None) -> None:
        """
        Set the line number of this instruction.
        If this is the first time that the instruction's line was set, the value will become the original line number.
        Args:
            line_number (int): The line number of this knitout instruction in a program.
            source (str, optional):
                The optional program name that this line derives from.
                This value is only set once (usually when setting the original line number).
                Defaults to None, not setting the program value.
        """
        if self._original_line_number is None:
            self._original_line_number = line_number
        if source is not None:
            self._source_program = source
        self._line_number = line_number

    def __str__(self) -> str:
        return self.comment_str

    def __repr__(self) -> str:
        if self._original_line_number is not None:
            return self.id_str()
        else:
            return str(self)

    def __hash__(self) -> int:
        """
        Returns:
            int: Unique integer based on the time that this instruction was created in the execution.
        """
        return hash(self._creation_time)

    _deepcopy_defaults: ClassVar[dict[str, Any]] = {
        "_original_line_number": None,
        "_line_number": None,
        "_source_program": None,
    }

    def _collect_deepcopy_defaults(self) -> dict[str, Any]:
        """Collect deepcopy defaults from the entire MRO."""
        defaults: dict[str, Any] = {}
        for cls in reversed(type(self).__mro__):
            if "_deepcopy_defaults" in cls.__dict__:
                defaults.update(cls._deepcopy_defaults)
        return defaults

    def __deepcopy__(self, memo: dict) -> Self:
        cls = self.__class__
        result = cast(Self, cls.__new__(cls))  # _creation_time assigned automatically
        memo[id(self)] = result
        defaults = self._collect_deepcopy_defaults()
        for k, v in self.__dict__.items():
            if k == "_creation_time":
                continue  # already set by __new__
            elif k in defaults:
                setattr(result, k, defaults[k])
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    _Lines_Made: ClassVar[int] = 0

    @staticmethod
    def _next_line() -> int:
        """
        Tick up the count of knitout_lines instantiated.
        Returns:
            int: The current line count before the number ticked up.
        """
        cur = Knitout_Line._Lines_Made
        Knitout_Line._Lines_Made += 1
        return cur


class Knitout_Comment_Line(Knitout_Line):
    """Represents a comment line in knitout."""

    def __init__(self, comment: str | Knitout_Line | Knitout_Comment_Line | None):
        """Initialize a comment line.

        Args:
            comment (None | str | Knitout_Line | Knitout_Comment_Line): The comment text, or a Knitout_Line to convert to a comment.
        """
        comment_str = (str(Knitout_Comment_Line.comment_str) if isinstance(comment, Knitout_Comment_Line) else f"No-Op:\t{comment}".strip()) if isinstance(comment, Knitout_Line) else comment
        super().__init__(comment_str)
        if isinstance(comment, Knitout_Line) and comment.has_line_number:
            self.set_line(comment.line_number, comment.source_program)

    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
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

        if self.original_instruction.has_line_number:
            self.set_line(self.original_instruction.line_number, self.original_instruction.source_program)

    def execute(self, machine_state: Knitout_Knitting_Machine) -> bool:
        return False  # No-Ops do not need to be included in executed knitout code.


class Knitout_BreakPoint(Knitout_Comment_Line):
    BP_TERM: str = "BreakPoint"

    def __init__(self, additional_comment: str | None = None):
        self.bp_comment: str | None = additional_comment
        super().__init__(f"{self.BP_TERM}: {additional_comment}")
