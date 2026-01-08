"""Module containing the Knitout_Debugger class."""

from __future__ import annotations

import os
import sys
import warnings
from collections.abc import Callable, Iterable
from enum import Enum
from typing import Protocol

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot

from knitout_interpreter._warning_stack_level_helper import get_user_warning_stack_level_from_knitout_interpreter_package
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_BreakPoint, Knitout_Comment_Line, Knitout_Line
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_warnings.Knitout_Warning import Knitout_BreakPoint_Condition_Warning


class Debug_Mode(Enum):
    """Enumeration of stepping modes for the debugger"""

    Step_Instruction = "step-instruction"
    Continue = "continue"
    Step_Carriage_Pass = "step-carriage-pass"


class Debuggable_Knitout_Execution(Protocol):
    """
    A protocol for knitout execution processes that can be debugged by the Knitout_Debugger class.
    """

    knitting_machine: Knitting_Machine  # The knitting machine that the debugged process is executing on.
    executed_instructions: list[Knitout_Line]  # The list of instructions that have been executed including the header, comments, and instructions.
    debugger: Knitout_Debugger | None  # The debugger attached to the execution process, if any.

    # noinspection PyPropertyDefinition
    @property
    def starting_new_carriage_pass(self) -> bool:
        """
        Returns:
            bool: True if the next instruction to be processed will initiate a new carriage pass, False otherwise.
        """
        ...


class Knitout_Debugger:
    """Debugger for knitout execution with breakpoints and stepping.

    Attributes:
        machine_snapshots (dict[int, Knitting_Machine_Snapshot]): Dictionary mapping line numbers that were paused on to the state of the knitting machine at that line.
    """

    def __init__(self) -> None:
        self._executer: Debuggable_Knitout_Execution | None = None
        self._breakpoints: set[int] = set()
        self._step_conditions: dict[str, Callable[[Knitout_Debugger, Knitout_Comment_Line | Knitout_Instruction], bool]] = {}
        self._carriage_pass_conditions: dict[str, Callable[[Knitout_Debugger, Knitout_Comment_Line | Knitout_Instruction], bool]] = {}
        self._debug_mode: Debug_Mode = Debug_Mode.Continue
        self._take_snapshots: bool = True
        self._condition_error: Exception | None = None
        self._stop_on_condition_error: bool = True
        self._raised_exceptions: set[BaseException] = set()
        self.machine_snapshots: dict[int, Knitting_Machine_Snapshot] = {}

    def attach_executer(self, executer: Debuggable_Knitout_Execution) -> None:
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
        print(f"Active Breakpoints: {sorted(self._breakpoints)}")
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
    def stop_on_condition_errors(self) -> bool:
        """
        Returns:
            bool: True if the debugger will stop when conditions trigger an exception. False, otherwise.
        """
        return self._stop_on_condition_error

    @property
    def current_line(self) -> int:
        """
        Returns:
            int: The current line that the debugger is processing.
        """
        return len(self.executed_instructions)

    @property
    def executed_instructions(self) -> list[Knitout_Line]:
        """
        Returns:
            list[Knitout_Line]: The instructions executed up to this point by the debugged process.
        """
        return [] if self._executer is None else self._executer.executed_instructions

    @property
    def knitting_machine(self) -> Knitting_Machine | None:
        """
        Returns:
            Knitting_Machine | None: The knitting machine the debugged process is running on or None if it has no debugging process.
        """
        return self._executer.knitting_machine if self._executer is not None else None

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
        self._stop_on_condition_error = False

    def pause_on_condition_exceptions(self) -> None:
        """
        Sets the debugger to stop when a breakpoint condition raises an exception.
        """
        self._stop_on_condition_error = True

    def disable_breakpoint(self, line_number: int) -> None:
        """
        Sets the debugger to ignore any breakpoint at the given line number.

        Args:
            line_number (int): The line number of the breakpoint to ignore.
        """
        if line_number in self._breakpoints:
            self._breakpoints.remove(line_number)

    def enable_breakpoint(self, line_number: int) -> None:
        """
        Allows the debugger to consider the breakpoint at the given line number.
        If a breakpoint was not already present, a breakpoint with no condition is set.

        Args:
            line_number (int): The line number of the breakpoint to consider.
        """
        self._breakpoints.add(line_number)

    def enable_step_condition(self, name: str, condition: Callable[[Knitout_Debugger, Knitout_Comment_Line | Knitout_Instruction], bool], is_carriage_pass_step: bool = False) -> None:
        """
        Adds the given condition to the debugger.

        Args:
            name (str): The unique name of the condition, used to deactivate it.
            condition (Callable[[Knitout_Debugger, Knitout_Comment_Line | Knitout_Instruction], bool]): The condition to be tested for pausing.
            is_carriage_pass_step (bool, optional): If true, only sets the condition on carriage pass steps. Defaults to setting the condition for all steps.
        """
        if is_carriage_pass_step:
            self._carriage_pass_conditions[name] = condition
        else:
            self._step_conditions[name] = condition

    def disable_condition(self, name: str, disable_steps: bool = True, disable_carriage_pass: bool = True) -> None:
        """
        Removes any step conditions by the given name.

        Args:
            name (str): The name of the condition to deactivate. If no condition exists by that name, nothing will happen.
            disable_steps (bool, optional): If True, disables condition on stepping. Defaults to True.
            disable_carriage_pass (bool, optional): If True, disables condition on carriage pass steps. Defaults to True.
        """
        if disable_steps and name in self._step_conditions:
            del self._step_conditions[name]
        if disable_carriage_pass and name in self._carriage_pass_conditions:
            del self._carriage_pass_conditions[name]

    def _breakpoint_is_active(self, line_number: int) -> bool:
        """
        Args:
            line_number (int): The line number to determine if the breakpoint is active and what conditions it must meet.

        Returns:
            bool: True if the given line number is an active breakpoint. False, otherwise.
        """
        return line_number in self._breakpoints

    @property
    def has_step_conditions(self) -> bool:
        """
        Returns:
            bool: True if the debugger has one or more conditions applied to it pausing at each step. False, otherwise.
        """
        return len(self._step_conditions) > 0

    @property
    def has_carriage_pass_conditions(self) -> bool:
        """
        Returns:
            bool: True if the debugger has one or more conditions applied to pausing at the beginning of a carriage pass. False, otherwise.
        """
        return len(self._carriage_pass_conditions) > 0

    def _meets_conditions(self, instruction: Knitout_Comment_Line | Knitout_Instruction, conditions: Iterable[Callable[[Knitout_Debugger, Knitout_Comment_Line | Knitout_Instruction], bool]]) -> bool:
        """
        Args:
            instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction to consider pausing before.
            conditions (Iterable[Callable[[Knitout_Debugger, Knitout_Comment_Line | Knitout_Instruction], bool]]: The conditions on pausing.

        Returns:
            bool: True if all the given conditions are met or a condition raises an error. False, otherwise.
        """
        for condition in conditions:
            try:
                if not condition(self, instruction):
                    return False
            except Exception as e:
                if self.stop_on_condition_errors:
                    self._condition_error = e
                    return True
                else:
                    warnings.warn(Knitout_BreakPoint_Condition_Warning(e), stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package())
        return True

    def _meets_step_conditions(self, instruction: Knitout_Comment_Line | Knitout_Instruction) -> bool:
        """
        Args:
            instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction to consider pausing before.

        Returns:
            bool: True if the all step-conditions are met or a condition error is encountered. False, otherwise.
        """
        return not self.has_step_conditions or self._meets_conditions(instruction, self._step_conditions.values())

    def meets_carriage_pass_conditions(self, instruction: Knitout_Comment_Line | Knitout_Instruction) -> bool:
        """
        Args:
            instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction to consider pausing before.

        Returns:
            bool: True if the all step-carriage-pass conditions are met or a condition error is encountered. False, otherwise.
        """
        return not self.has_carriage_pass_conditions or self._meets_conditions(instruction, self._carriage_pass_conditions.values())

    def pause_on_step(self, instruction: Knitout_Comment_Line | Knitout_Instruction) -> bool:
        """
        Args:
            instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction to pause before.

        Returns:
            bool: True if the debugger should pause before the next instruction because of step-mode. False, otherwise.
        """
        return isinstance(instruction, (Pause_Instruction, Knitout_BreakPoint)) or (self.take_step and self._meets_step_conditions(instruction))

    def pause_on_carriage_pass(self, instruction: Knitout_Comment_Line | Knitout_Instruction) -> bool:
        """
        Args:
            instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction to pause before.

        Returns:
            bool: True if the debugger should pause before the next instruction because of step-carriage-pass-mode. False, otherwise.
        """
        return self._executer is not None and self.take_carriage_pass_step and self._executer.starting_new_carriage_pass and self.meets_carriage_pass_conditions(instruction)

    def should_break(self, instruction: Knitout_Comment_Line | Knitout_Instruction) -> bool:
        """
        Args:
            instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction or comment that is about to be executed.

        Returns:
            bool: True if the debugger should pause execution given the current state of the knitting machine and upcoming instruction. False otherwise.
        """
        if self._executer is None:
            return False
        elif self.pause_on_step(instruction) or self.pause_on_carriage_pass(instruction):
            return True
        # Test instruction for active breakpoint
        next_line_number = instruction.original_line_number if instruction.original_line_number is not None else self.current_line
        return self._breakpoint_is_active(next_line_number)

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
            executed_program: list[Knitout_Line] = self.executed_instructions  # noqa: F841
            if self.taking_snapshots:
                self.machine_snapshots[knitout_line] = Knitting_Machine_Snapshot(knitting_machine)
            if self._is_interactive_debugger_attached():
                print(f"\n{'=' * 70}")
                if self.take_step:
                    print(f"Stepped to line {knitout_line}: {knitout_instruction}")
                elif isinstance(knitout_instruction, Knitout_BreakPoint):
                    print(f"Knitout Program has a breakpoint at this line: {knitout_line}")
                    if knitout_instruction.bp_comment is not None:
                        print(f"\t BreakPoint Comment: {knitout_instruction.bp_comment}")
                elif isinstance(knitout_instruction, Pause_Instruction):
                    print(f"Knitout Program paused at this line: {knitout_line}")
                elif self.take_carriage_pass_step and self._executer.starting_new_carriage_pass:
                    print(f"Knitout Stopped Before Carriage Pass Starting on line {knitout_line}: {knitout_instruction}")
                else:
                    print(f"Knitout Breakpoint Hit at Line {knitout_line}: {knitout_instruction}")
                    if self._condition_error is not None:
                        print(f"Breakpoint Condition triggered an exception:\n\t{self._condition_error}")
                self.print_usage_guide()
                breakpoint()  # Only called when IDE debugger is active
                self._condition_error = None  # reset condition exception until next time a breakpoint is hit

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
            executed_program: list[Knitout_Line] = self.executed_instructions  # noqa: F841
            if self.taking_snapshots:
                self.machine_snapshots[knitout_line] = Knitting_Machine_Snapshot(knitting_machine)
            if self._is_interactive_debugger_attached():
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
        print("knitout_debugger.step_carriage_pass()     # Step to next carriage pass")
        print("knitout_debugger.continue_knitout()          # Continue to next breakpoint")
        print("knitout_debugger.enable_snapshots()  # Enable the debugger to take snapshots of the knitting machine when breakpoints are hit")
        print("knitout_debugger.disable_snapshots()  # Disable snapshots of the knitting machine state")
        print("knitout_debugger.status()        # Show debugger status")
        print("knitout_debugger.disable_breakpoint(N)   # Disable any breakpoint at line N")
        print("knitout_debugger.enable_breakpoint(N) # Enable a breakpoint breakpoint at line N.")
        print("knitout_debugger.enable_step_condition(name, condition, step or carriage pass ste)   # Enable the debugger to step on a given named condition")
        print("knitout_debugger.disabled_step_condition(name)   # Disable any stepping conditions by the given named")

    @staticmethod
    def _is_interactive_debugger_attached() -> bool:
        """Check if an interactive debugger session is active.

        Uses multiple heuristics to detect interactive debugging across
        different IDEs and platforms (PyCharm, VSCode, etc.).

        Returns:
            bool: True if an interactive debugger session is active. False otherwise.
        """
        # No trace function = no debugger
        if sys.gettrace() is None:
            return False

        # Check: CI/automated environment detection (if these exist, this session is not interactive and shouldn't be debugged)
        ci_indicators = {
            "CI",
            "CONTINUOUS_INTEGRATION",  # Generic CI
            "GITHUB_ACTIONS",  # GitHub Actions
            "TRAVIS",
            "CIRCLECI",  # Other CI systems
            "JENKINS_HOME",
        }
        if any(var in os.environ for var in ci_indicators):
            return False

        # Check: Known debugger modules
        trace = sys.gettrace()
        if trace is not None:
            trace_module = getattr(trace, "__module__", "")
            interactive_debuggers = ["pydevd", "pdb", "bdb", "debugpy", "_pydevd_bundle"]
            if any(debugger in trace_module for debugger in interactive_debuggers):
                return True

        # Check: IDE environment variables
        ide_indicators = {
            "PYCHARM_HOSTED",  # PyCharm
            "PYDEVD_LOAD_VALUES_ASYNC",  # PyCharm debugger
            "VSCODE_PID",  # VSCode
        }
        if any(var in os.environ for var in ide_indicators):
            return True

        # Check: TTY as fallback. An interactive console found (only reliable on Unix)
        return sys.stdin.isatty()
