"""Collection of warnings related to knitout processing"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass


class Knitout_Warning(RuntimeWarning):
    """Base class for warnings related to knitout operations that can be handled gracefully.
    This class provides standardized warning message formatting and supports configurable instruction ignoring behavior for different types of machine state issues.
    """

    def __init__(self, message: str, ignore_instructions: bool = False) -> None:
        """Initialize a knitting machine warning with formatted message.

        Args:
            message (str): The descriptive warning message about the machine state issue.
            ignore_instructions (bool, optional): Whether this warning indicates that the operation should be ignored. Defaults to False.
        """
        ignore_str = ""
        if ignore_instructions:
            ignore_str = ". Ignoring Operation."
        self.message = f"\n\t{self.__class__.__name__}: {message}{ignore_str}"
        super().__init__(self.message)


class Reorder_Carriage_Pass_Warning(Knitout_Warning):
    """Warning raised when risky attempt to reorder a carriage pass."""

    def __init__(self, carriage_pass: Carriage_Pass) -> None:
        self.carriage_pass: Carriage_Pass = carriage_pass
        super().__init__(f"Re-ordering a directed carriage pass may have unintended results: {carriage_pass}")


class Knitout_BreakPoint_Condition_Warning(Knitout_Warning):
    """Warning raised when a knitout debugger ignores a conditional breakpoint where the condition caused an exception"""

    def __init__(self, exception: BaseException) -> None:
        self.exception: BaseException = exception
        super().__init__(f"Knitout Breakpoint condition triggered an exception:\n\t{exception}")


class Missed_Snapshot_Warning(Knitout_Warning):
    """Warning raised when knit execution is set with a target line that may have already passed."""

    def __init__(self, target_line: int, current_line: int) -> None:
        super().__init__(f"Snapshot on target line {target_line} likely missed. Execution on line {current_line}")
