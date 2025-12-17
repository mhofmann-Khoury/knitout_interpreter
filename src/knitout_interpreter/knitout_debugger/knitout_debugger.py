"""Module containing the Knitout_Debugger class."""

from __future__ import annotations

import sys
import warnings
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, cast

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot

from knitout_interpreter._warning_stack_level_helper import get_user_warning_stack_level_from_knitout_interpreter_package
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_BreakPoint, Knitout_Comment_Line, Knitout_Line
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_warnings.Knitout_Warning import Knitout_BreakPoint_Condition_Warning

if TYPE_CHECKING:
    from knitout_interpreter.knitout_execution import Knitout_Executer


class Debug_Mode(Enum):
    """Enumeration of stepping modes for the debugger"""

    Step_Instruction = "step-instruction"
    Continue = "continue"
    Step_Carriage_Pass = "step-carriage-pass"


class Knitout_Debugger:
    """Debugger for knitout execution with breakpoints and stepping.

    Attributes:
        breakpoints (dict[int, Callable[[Knitting_Machine, Knitout_Line], bool] | None]): Dictionary of breakpoint line numbers and conditions for activation.
        machine_snapshots (dict[int, Knitting_Machine_Snapshot]): Dictionary mapping line numbers that were paused on to the state of the knitting machine at that line.
    """

    def __init__(self) -> None:
        self._executer: Knitout_Executer | None = None
        self.breakpoints: dict[int, Callable[[Knitting_Machine, Knitout_Line], bool] | None] = {}  # line_num -> condition function
        self._disabled_breakpoints: set[int] = set()
        self._debug_mode: Debug_Mode = Debug_Mode.Continue
        self._is_active: bool = False
        self._take_snapshots: bool = True
        self.machine_snapshots: dict[int, Knitting_Machine_Snapshot] = {}
        self._condition_exception: Exception | None = None
        self._stop_on_condition_exceptions: bool = True
        self._raised_exceptions: set[BaseException] = set()

    def attach_executer(self, executer: Knitout_Executer) -> None:
        """
        Attaches the given executer to this debugger.

        Args:
            executer (Knitout_Executer): The executer to attach to this debugger.
        """
        self._executer = executer

    def detach_executer(self) -> None:
        """
        Detaches the current executer from this debugger.
        """
        self._executer = None

    def status(self) -> None:
        """
        Prints out the status of the debugger to console.
        """
        print(f"\n{'=' * 60}")
        print("Knitout Debugger Status")
        print(f"{'=' * 60}")
        print(f"Mode: {self._debug_mode.value}")
        print(f"Current Line: {self.current_line}")
        print(f"Active Breakpoints: {sorted(self.breakpoints.keys())}")
        print(f"Disabled Breakpoints: {sorted(self._disabled_breakpoints)}")
        print(f"{'=' * 60}\n")

    @property
    def take_step(self) -> bool:
        """
        Returns:
            bool: True if the debugger is set to step on every instruction line. False, otherwise.
        """
        return self._debug_mode is Debug_Mode.Step_Instruction

    @property
    def take_carriage_pass_step(self) -> bool:
        """
        Returns:
            bool: True if the debugger is set to step until the end of the current carriage pass. False, otherwise.
        """
        return self._debug_mode is Debug_Mode.Step_Carriage_Pass

    @property
    def continue_to_end(self) -> bool:
        """
        Returns:
            bool: True if the debugger is set to continue to the next active breakpoint. False, otherwise.
        """
        return self._debug_mode is Debug_Mode.Continue

    @property
    def taking_snapshots(self) -> bool:
        """
        Returns:
            bool: True if the debugger is set to take snapshots of the knitting machine state when paused. False, otherwise.

        Notes:
            Snapshots are stored in the debugger's machine_snapshots dictionary.
        """
        return self._take_snapshots

    @property
    def stop_on_condition_exceptions(self) -> bool:
        """
        Returns:
            bool: True if the debugger will stop on breakpoints where the condition triggers an exception. False, otherwise.
        """
        return self._stop_on_condition_exceptions

    def step(self, step_carriage_passes_only: bool = False) -> None:
        """
        Sets the debugger to a stepping mode. By default, enter instruction level step mode.
        Args:
            step_carriage_passes_only (bool, optional): If True, debugger set to step over carriage passes, instead of every line. Defaults to stepping every line (False).
        """
        if step_carriage_passes_only:
            self._debug_mode = Debug_Mode.Step_Carriage_Pass
        else:
            self._debug_mode = Debug_Mode.Step_Instruction

    def step_carriage_pass(self) -> None:
        """
        Sets the debugger to step over each carriage pass unless a breakpoint is hit inside the carriage pass.
        """
        self.step(step_carriage_passes_only=True)

    def continue_knitout(self) -> None:
        """
        Sets the debugger to continue to the next breakpoint or end of the knitout program.
        """
        self._debug_mode = Debug_Mode.Continue

    def enable_snapshots(self) -> None:
        """
        Sets the debugger to take snapshots of the knitting machine state whenever it pauses.
        """
        self._take_snapshots = True

    def disable_snapshots(self) -> None:
        """
        Sets the debugger to not take snapshots of the knitting machine state.
        """
        self._take_snapshots = False

    def ignore_condition_exceptions(self) -> None:
        """
        Sets the debugger to ignore condition exceptions and continue over these breakpoints.
        """
        self._stop_on_condition_exceptions = False

    def pause_on_condition_exceptions(self) -> None:
        """
        Sets the debugger to stop when a breakpoint condition raises an exception.
        """
        self._stop_on_condition_exceptions = True

    @property
    def current_line(self) -> int:
        """
        Returns:
            int: The current line that the debugger is processing.
        """
        if self._executer is None:
            return 0
        else:
            return self._executer.execution_length

    def set_breakpoint(self, line_number: int, condition: Callable[[Knitting_Machine, Knitout_Line], bool] | None = None) -> None:
        """Set a breakpoint at a specific knitout line number with an optional condition for breaking.

        Args:
            line_number (int): Line number in the knitout file (1-indexed)
            condition (Callable[[Knitting_Machine, Knitout_Line], bool], optional): Conditional function that takes (machine, instruction) and returns bool. Defaults to no condition.
        """
        if line_number in self._disabled_breakpoints:
            self._disabled_breakpoints.remove(line_number)
        self.breakpoints[line_number] = condition

    def disable_breakpoint(self, line_number: int) -> None:
        """
        Sets the debugger to ignore any breakpoint at the given line number.

        Args:
            line_number (int): The line number of the breakpoint to ignore.
        """
        if line_number in self.breakpoints:
            self._disabled_breakpoints.add(line_number)

    def enable_breakpoint(self, line_number: int) -> None:
        """
        Allows the debugger to consider the breakpoint at the given line number.
        If a breakpoint was not already present, a breakpoint with no condition is set.

        Args:
            line_number (int): The line number of the breakpoint to consider.
        """
        if line_number in self._disabled_breakpoints:
            self._disabled_breakpoints.remove(line_number)
        if line_number not in self.breakpoints:
            self.set_breakpoint(line_number)

    def clear_breakpoint(self, line_number: int) -> None:
        """Remove breakpoint at line number. If no breakpoint is set at that line number, nothing happens.

        Args:
            line_number (int): Line number of the breakpoint to remove.
        """
        if line_number in self._disabled_breakpoints:
            self._disabled_breakpoints.remove(line_number)
        if line_number in self.breakpoints:
            del self.breakpoints[line_number]

    def breakpoint_is_active(self, line_number: int) -> tuple[bool, Callable[[Knitting_Machine, Knitout_Line], bool] | None]:
        """
        Args:
            line_number (int): The line number to determine if the breakpoint is active and what conditions it must meet.

        Returns:
            tuple[bool, None | Callable[[Knitting_Machine, Knitout_Line], bool]]:
                A tuple of two values:
                * If the first value is True, the breakpoint at the line number is enabled.
                * The second value will be the conditional of the enabled break point or None if it is not conditioned or the breakpoint is not enabled.
        """
        if line_number in self._disabled_breakpoints or line_number not in self.breakpoints:
            return False, None
        else:
            return True, self.breakpoints[line_number]

    def should_break(self, instruction: Knitout_Line) -> bool:
        """Determine if we should break at this line.

        Args:
            instruction (Knitout_Line): Knitout_Line instruction that will be executed on this line.

        Returns:
            bool: True if the breakpoint should pause execution given the current state of the knitting machine and upcoming instruction. False otherwise.
        """
        if self._executer is None or (not self._executer.executing_current_carriage_pass and isinstance(instruction, Needle_Instruction)):
            # Don't break on needle instructions until they are being executed with the completely formed carriage pass.
            return False
        elif self.take_step or isinstance(instruction, (Pause_Instruction, Knitout_BreakPoint)):
            return True  # Pause in step mode or on pause and breakpoint instructions
        # Test instruction for active breakpoint
        next_line_number = instruction.original_line_number if instruction.original_line_number is not None else self.current_line
        bp_is_active, bp_condition = self.breakpoint_is_active(next_line_number)
        if bp_is_active:
            if bp_condition is None:
                return True
            try:
                if bp_condition(self._executer.knitting_machine, instruction):
                    return True
            except Exception as e:
                if self.stop_on_condition_exceptions:
                    self._condition_exception = e
                    return True
                else:
                    warnings.warn(Knitout_BreakPoint_Condition_Warning(e), stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package())
        return False

    def debug_instruction(self, knitout_instruction: Knitout_Comment_Line | Knitout_Instruction) -> None:
        """
        The debugging protocol given the state of the debugger and the instruction about to be executed.

        Args:
            knitout_instruction (Knitout_Comment_Line | Knitout_Instruction): The knitout instruction to pause the debugger on or continue.
        """
        if self._executer is not None and self.should_break(knitout_instruction):
            # These variables will be visible in the debugger
            # noinspection PyUnusedLocal
            knitout_debugger: Knitout_Debugger = self  # noqa: F841
            knitout_line: int = knitout_instruction.original_line_number if knitout_instruction.original_line_number is not None else self.current_line
            knitting_machine: Knitting_Machine = self._executer.knitting_machine
            # noinspection PyUnusedLocal
            current_carriage_pass: Carriage_Pass | None = self._executer.current_carriage_pass  # noqa: F841
            # noinspection PyUnusedLocal
            executed_program: list[Knitout_Instruction | Knitout_Comment_Line] = self._executer.executed_program  # noqa: F841
            if self.taking_snapshots:
                self.machine_snapshots[knitout_line] = Knitting_Machine_Snapshot(knitting_machine)
            if sys.gettrace() is not None and sys.stdin.isatty():  # Check if IDE debugger is attached
                print(f"\n{'=' * 70}")
                if isinstance(knitout_instruction, Knitout_BreakPoint):
                    print(f"Knitout Program has a breakpoint at this line: {knitout_line}")
                    if knitout_instruction.bp_comment is not None:
                        print(f"\t BreakPoint Comment: {knitout_instruction.bp_comment}")
                elif isinstance(knitout_instruction, Pause_Instruction):
                    print(f"Knitout Program paused at this line: {knitout_line}")
                else:
                    print(f"Knitout Breakpoint Hit at Line {knitout_line}: {knitout_instruction}")
                    if self._condition_exception is not None:
                        print(f"Breakpoint Condition triggered an exception:\n\t{self._condition_exception}")
                self.print_usage_guide()
                breakpoint()  # Only called when IDE debugger is active
                self._condition_exception = None  # reset condition exception until next time a breakpoint is hit

    def debug_current_carriage_pass(self) -> None:
        """
        The debugging protocol given the state of the debugger and the instruction about to be executed.
        """
        if self._executer is not None and self.take_carriage_pass_step:
            # These variables will be visible in the debugger
            # noinspection PyUnusedLocal
            knitout_debugger: Knitout_Debugger = self  # noqa: F841
            # noinspection PyUnusedLocal
            executed_program: list[Knitout_Instruction | Knitout_Comment_Line] = self._executer.executed_program  # noqa: F841
            current_carriage_pass: Carriage_Pass = cast(Carriage_Pass, self._executer.current_carriage_pass)
            knitout_instruction: Knitout_Instruction | Knitout_Comment_Line = current_carriage_pass.first_instruction
            knitout_line: int = knitout_instruction.original_line_number if knitout_instruction.original_line_number is not None else self.current_line
            knitting_machine: Knitting_Machine = self._executer.knitting_machine
            if self.taking_snapshots:
                self.machine_snapshots[knitout_line] = Knitting_Machine_Snapshot(knitting_machine)
            if sys.gettrace() is not None and sys.stdin.isatty():  # Check if IDE debugger is attached
                print(f"\n{'=' * 70}")
                print(f"Knitout Stopped Before Carriage Pass Starting on line {knitout_line}: {knitout_instruction}")
                self.print_usage_guide()
                breakpoint()  # Only called when IDE debugger is active
                self._condition_exception = None  # reset condition exception until next time a breakpoint is hit

    def debug_exception(self, knitout_instruction: Knitout_Comment_Line | Knitout_Instruction, exception: BaseException) -> None:
        """
        Trigger a breakpoint immediately after a knitout instruction causes an exception. Raise the exception after the debugger continues.

        Args:
            knitout_instruction (Knitout_Comment_Line | Knitout_Instruction): The knitout instruction that triggered the exception.
            exception (BaseException): The exception that the debugger will pause on.
        """
        if self._executer is not None and exception not in self._raised_exceptions:
            # These variables will be visible in the debugger
            # noinspection PyUnusedLocal
            knitout_debugger: Knitout_Debugger = self  # noqa: F841
            knitout_line: int = knitout_instruction.original_line_number if knitout_instruction.original_line_number is not None else self.current_line
            knitting_machine: Knitting_Machine = self._executer.knitting_machine
            # noinspection PyUnusedLocal
            current_carriage_pass: Carriage_Pass | None = self._executer.current_carriage_pass  # noqa: F841
            # noinspection PyUnusedLocal
            executed_program: list[Knitout_Instruction | Knitout_Comment_Line] = self._executer.executed_program  # noqa: F841
            if self.taking_snapshots:
                self.machine_snapshots[knitout_line] = Knitting_Machine_Snapshot(knitting_machine)
            if sys.gettrace() is not None and sys.stdin.isatty():  # Check if IDE debugger is attached
                print(f"\n{'=' * 70}")
                print(f"Knitout Paused on {exception.__class__.__name__} raised at Line {knitout_line}: {knitout_instruction}")
                print(f"\t{exception}")
                self.print_usage_guide()
                breakpoint()  # Only called when IDE debugger is active
            self._raised_exceptions.add(exception)

    @staticmethod
    def print_usage_guide() -> None:
        """Helper function that prints out the Knitout Debugger Breakpoint command line interface and Usage Guide."""
        print(f"\n{'=' * 10}Knitout Debugger Options{'=' * 20}")
        print("knitout_debugger.step()          # Step to next instruction")
        print("knitout_debugger.continue_knitout()          # Continue to next breakpoint")
        print("knitout_debugger.step_carriage_pass()     # Step to next carriage pass")
        print("knitout_debugger.enable_snapshots()  # Enable the debugger to take snapshots of the knitting machine when breakpoints are hit")
        print("knitout_debugger.disable_snapshots()  # Disable snapshots of the knitting machine state")
        print("knitout_debugger.status()        # Show debugger status")
        print("knitout_debugger.set_breakpoint(N)   # Set breakpoint at line N")
        print("knitout_debugger.clear_breakpoint(N) # Remove breakpoint at line N")
        print("knitout_debugger.disable_breakpoint(N)   # Temporarily disable an breakpoint at line N but does not remove it or any conditions set")
        print("knitout_debugger.enable_breakpoint(N) # Re-enable a breakpoint breakpoint at line N. If no breakpoint is there, a new breakpoint is set")
