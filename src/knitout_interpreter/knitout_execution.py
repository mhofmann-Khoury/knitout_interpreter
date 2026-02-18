"""Module containing the knitout executer class"""

from __future__ import annotations

import warnings
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, TypeVar

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.Knitting_Machine_Snapshot import Knitting_Machine_Snapshot
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.machine_component_protocol import Machine_Component
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import Violation, ViolationAction, ViolationResponse

from knitout_interpreter._warning_stack_level_helper import get_user_warning_stack_level_from_knitout_interpreter_package
from knitout_interpreter.debugger.debug_decorator import debug_knitout_instruction
from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass, carriage_pass_typed_to_first_instruction
from knitout_interpreter.knitout_execution_structures.knitout_header import Knitting_Machine_Header
from knitout_interpreter.knitout_execution_structures.Knitout_Knitting_Machine import Knitout_Knitting_Machine, Knitout_Machine_Specification
from knitout_interpreter.knitout_execution_structures.knitout_loops import Knitout_Loop
from knitout_interpreter.knitout_execution_structures.knitout_program import Knitout_Program
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.Header_Line import Knitout_Version_Line
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line, Knitout_Line, Knitout_No_Op
from knitout_interpreter.knitout_operations.needle_instructions import Drop_Instruction, Knit_Pass_Instruction, Miss_Instruction, Needle_Instruction, Split_Instruction, Xfer_Instruction
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_warnings.Knitout_Warning import Missed_Snapshot_Warning

if TYPE_CHECKING:
    from knitout_interpreter.debugger.knitout_debugger import Knitout_Debugger

Knitout_LoopT = TypeVar("Knitout_LoopT", bound=Knitout_Loop)


class Knitout_Executer(Machine_Component[Knitout_LoopT]):
    """A class used to execute a set of knitout instructions on a virtual knitting machine.
    The instructions are processed, organized to isolate the header, verified on the knitting machine, and no-op operations are converted into comments.
    The execution process can optionally be debugged by attaching a debugger.
    The execution process can have optional snapshots of the knitting machine taken at specified line numbers.

    Attributes:
        process (list[Knitout_Instruction | Carriage_Pass]): The ordered list of instructions and carriage passes executed in the knitting process.
        executed_header (Knitting_Machine_Header): The header that creates this knitting machine based on the header lines specified and the knitting machine specified at initialization.
        executed_instructions (Knitout_Program): The instructions that have been executed so far and updated the knitting machine state.
        debugger (Knitout_Debugger | None): The optional debugger attached to this knitout process.
    """

    def __init__(
        self,
        knitout_program: Sequence[Knitout_Line] | str,
        knitting_machine: Knitout_Knitting_Machine[Knitout_LoopT] | Knitout_Machine_Specification | None = None,
        debugger: Knitout_Debugger | None = None,
        snapshot_targets: Sequence[int] | set[int] | None = None,
        relax_violations: bool | Iterable[Violation] = False,
        knitout_version: int = 2,
    ):
        """Initialize the knitout executer.

        Args:
            knitout_program (Sequence[Knitout_Line] | str): The knitout lines to executed or a filename to parse into a knitout program.
            knitting_machine (Knitting_Machine, optional): The virtual knitting machine to execute instructions on. Defaults to the default Knitting Machine with no prior operations.
            debugger (Knitout_Debugger, optional): The debugger to attach to this knitout execution process. Defaults to having no debugger.
            snapshot_targets (Sequence[int] | set[int], optional): The line numbers to create machine snapshots from. Defaults to no snapshot targets.
            relax_violations (bool | Iterable[Violation], optional): If True, all violations are relaxed. If violations are given, those violations are relaxed. Defaults to False (full validation).
            knitout_version (int, optional): The knitout version to use. Defaults to 2.

        Raises:
            FileNotFoundError: If knitout_program is given as a filename but the file cannot be found.
            Knitout_ParseError: If the knitout_program cannot be parsed from the given file.
            Incomplete_Knitout_Line_Error: If a line in the knitout_program is incomplete and cannot be parsed into a full instruction.
        """
        if isinstance(knitout_program, str):
            self.knitout_program: Knitout_Program = parse_knitout(knitout_program, pattern_is_file=True)
        else:
            self.knitout_program = Knitout_Program(knitout_program, default_version=knitout_version)
        self.executed_header: Knitting_Machine_Header = Knitting_Machine_Header(knitting_machine, version=self.knitout_version)
        if isinstance(knitting_machine, Knitout_Knitting_Machine):
            self._knitting_machine: Knitout_Knitting_Machine[Knitout_LoopT] = knitting_machine
        else:
            self.executed_header.extract_header(self.knitout_program)
            self._knitting_machine: Knitout_Knitting_Machine[Knitout_LoopT] = Knitout_Knitting_Machine[Knitout_LoopT](machine_specification=self.executed_header.specification)
        if not isinstance(relax_violations, bool):
            self.relax_validation_policy(relax_violations)
        elif relax_violations:
            self.relax_validation_policy()
        self.debugger: Knitout_Debugger | None = None
        if debugger is not None:
            self.attach_debugger(debugger)
        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self._carriage_passes: list[Carriage_Pass] = []
        self._left_most_position: int | None = None
        self._right_most_position: int | None = None
        self.executed_instructions: Knitout_Program = self.knitout_program.new_header_program()
        self._current_carriage_pass: Carriage_Pass | None = None  # The carriage pass currently being formed in execution of the knitout program.
        self._starting_new_cp: bool = False  # If True, the next instruction initiates a new carriage pass.
        self._snapshot_targets: set[int] = set(snapshot_targets) if snapshot_targets is not None else set()  # User specified line numbers to take a snapshot of the knitting machine at
        self.snapshots: dict[int, Knitting_Machine_Snapshot[Knitout_LoopT]] = {}  # Mapping of line numbers to the snapshots taken during the execution.
        self.test_and_organize_instructions()

    @property
    def knitout_version(self) -> int:
        """
        Returns:
            int: The knitout version being executed.
        """
        return self.knitout_program.version_line.version

    @property
    def version_line(self) -> Knitout_Version_Line:
        """Get the version line for the executed knitout.

        Returns:
            Knitout_Version_Line: The version line for the executed knitout.
        """
        return Knitout_Version_Line(self.knitout_version)

    @property
    def knitting_machine(self) -> Knitout_Knitting_Machine[Knitout_LoopT]:
        """
        Returns:
            Knitout_Knitting_Machine[Knitout_LoopT]: The knitting machine that the program is executing on.
        """
        return self._knitting_machine

    @property
    def resulting_knit_graph(self) -> Knit_Graph[Knitout_LoopT]:
        """Get the knit graph resulting from instruction execution.

        Returns:
            Knit_Graph[Knitout_Loop]: Knit Graph that results from execution of these instructions.
        """
        return self.knitting_machine.knit_graph

    @property
    def carriage_passes(self) -> list[Carriage_Pass]:
        """Get the carriage passes from this execution.

        Returns:
            list[Carriage_Pass]: The carriage passes resulting from this execution in execution order.
        """
        return self._carriage_passes

    @property
    def execution_time(self) -> int:
        """Get the execution time as measured by carriage passes.

        Returns:
            int: Count of carriage passes in process as a measure of knitting time.
        """
        return len(self._carriage_passes)

    @property
    def execution_length(self) -> int:
        """
        Returns:
            int: The number of lines in the completed execution. This includes the lines for the header, all comments, and all executed instructions.
        """
        return len(self.executed_instructions)

    @property
    def left_most_position(self) -> int | None:
        """Get the leftmost needle position used in execution.

        Returns:
            int | None: The position of the left most needle used in execution, or None if no needles were used.
        """
        return self._left_most_position

    @property
    def right_most_position(self) -> int | None:
        """Get the rightmost needle position used in execution.

        Returns:
            int | None: The position of the right most needle used in the execution, or None if no needles were used.
        """
        return self._right_most_position

    @property
    def current_carriage_pass(self) -> Carriage_Pass | None:
        """
        Returns:
            None | Carriage_Pass: The carriage pass currently being formed in the knitout execution or None if no carriage pass is being formed.
        """
        return self._current_carriage_pass

    @property
    def starting_new_carriage_pass(self) -> bool:
        """
        Returns:
            bool: True if the next instruction to be processed will initiate a new carriage pass, False otherwise.
        """
        return self._starting_new_cp

    def attach_debugger(self, debugger: Knitout_Debugger | None = None) -> None:
        """
        Attaches the given debugger to this knitout execution.
        Args:
            debugger (Knitout_Debugger, optional): The debugger to attach to this knitout execution process. Defaults to attaching a new default debugger.
        """
        if debugger is None:
            debugger = Knitout_Debugger()
        self.debugger = debugger
        self.debugger.attach_executer(self)

    def detach_debugger(self) -> None:
        """
        Detaches the current debugger from this knitout execution.
        """
        if self.debugger is not None:
            self.debugger.detach_executer()
        self.debugger = None

    def enable_snapshot(self, target_line: int) -> None:
        """
        Sets the execution to take a snapshot when it reaches the given line.

        Args:
            target_line (int): The target line number to take a snapshot on

        Warns:
             Missed_Snapshot_Warning: If the target line has been passed.
        """
        self._snapshot_targets.add(target_line)
        if len(self.executed_instructions) > target_line:
            warnings.warn(Missed_Snapshot_Warning(target_line, len(self.executed_instructions)), stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package())

    def disable_snapshot(self, target_line: int, remove_existing_snapshot: bool = False) -> None:
        """
        Removes target snapshot on given line number.
        Args:
            target_line (int): The target line number that should not have a snapshot taken.
            remove_existing_snapshot (bool, optional): If True, any snapshot already taken on the given line is deleted. Defaults to False and keeping that snapshot.
        """
        if target_line in self._snapshot_targets:
            self._snapshot_targets.remove(target_line)
        if remove_existing_snapshot and target_line in self.snapshots:
            del self.snapshots[target_line]

    def relax_validation_policy(self, violations: Iterable[Violation] = Violation, include_warnings: bool = False) -> None:
        """
        Update the Knitting_Machine_Error_Policy of the execution knitting machine to relax the given violations.

        Args:
            violations (Sequence[Violation], optional): The violations to relax. Defaults to all violations.
            include_warnings (bool, optional): If True, warning will be raised for violations. Defaults to False.
        """
        action: ViolationAction = ViolationAction.WARN if include_warnings else ViolationAction.IGNORE
        for violation in violations:
            self.knitting_machine.set_response_for(violation, ViolationResponse(action))

    def test_and_organize_instructions(self) -> None:
        """Test the given execution and organize the instructions in the class structure.

        This method processes all instructions, organizing them into carriage passes and handling any errors that occur during execution.

        """
        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self._current_carriage_pass = None
        for _i, instruction in enumerate(self.knitout_program.program_body):
            self._process_next_instruction(instruction)
        self._end_program()

    def write_executed_instructions(self, filename: str) -> None:
        """Write a file with the organized knitout instructions.

        Args:
            filename (str): The file path to write the executed instructions to.
        """
        with open(filename, "w") as file:
            file.writelines([str(instruction) for instruction in self.executed_instructions])

    def _execute_current_carriage_pass(self, next_cp_instruction: Xfer_Instruction | Split_Instruction | Drop_Instruction | Knit_Pass_Instruction | Miss_Instruction | None = None) -> None:
        """Execute carriage pass with an implied racking operation on the given knitting machine.

        Args:
            next_cp_instruction (Xfer_Instruction | Split_Instruction | Drop_Instruction| Knit_Pass_Instruction | Miss_Instruction | None, optional):
                The next instruction at the beginning of the carriage pass that will follow the current carriage pass. Defaults to no carriage pass instruction following this pass.

        Notes:
            Ordering xfers in a rightward ascending direction.
        """
        if self.current_carriage_pass is None:
            return
        self._execute_and_add_instruction(self.current_carriage_pass.rack_instruction())
        if self.current_carriage_pass.xfer_pass:
            self.current_carriage_pass.direction = Carriage_Pass_Direction.Rightward  # default xfers to be in ascending order
        self._starting_new_cp = True
        for instruction in self.current_carriage_pass:
            self._execute_and_add_instruction(instruction)
            self._starting_new_cp = False  # set to false after first instruction is processed.
        self.process.append(self.current_carriage_pass)
        self.carriage_passes.append(self.current_carriage_pass)
        left, right = self.current_carriage_pass.carriage_pass_range
        self._left_most_position = min(self._left_most_position, left) if self._left_most_position is not None else left
        self._right_most_position = max(self._right_most_position, right) if self._right_most_position is not None else right
        if next_cp_instruction is not None:
            self._current_carriage_pass = carriage_pass_typed_to_first_instruction(next_cp_instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
        else:
            self._current_carriage_pass = None

    def _take_snapshot(self, instruction: Knitout_Instruction | Knitout_Comment_Line) -> None:
        """
        Takes a snapshot at the current state if the instruction's line number is in the snapshot targets.
        Args:
            instruction (Knitout_Instruction | Knitout_Comment_Line): The instruction to take a snapshot of.
        """
        if instruction.has_line_number and instruction.original_line_number in self._snapshot_targets:
            self.snapshots[instruction.original_line_number] = Knitting_Machine_Snapshot[Knitout_LoopT](self.knitting_machine)

    @debug_knitout_instruction
    def _add_non_executable_instruction_to_execution(self, instruction: Knitout_Instruction | Knitout_Comment_Line) -> None:
        self._take_snapshot(instruction)
        self.executed_instructions.append_line(instruction)

    @debug_knitout_instruction
    def _execute_and_add_instruction(self, instruction: Knitout_Instruction | Knitout_Comment_Line) -> None:
        if isinstance(instruction, (Knitout_Comment_Line | Pause_Instruction)):
            self.executed_instructions.append_line(instruction)
        else:
            updated_machine = instruction.execute(self.knitting_machine)
            if updated_machine:
                if not isinstance(instruction, (Needle_Instruction, Knitout_Comment_Line)):  # Not in a carriage pass and not a comment, so add this to the process on its own.
                    self.process.append(instruction)
                self.executed_instructions.append_line(instruction)
            elif instruction.has_line_number:  # Didn't update but was in the original program, so convert it to a no-op comment
                self.executed_instructions.append_line(Knitout_No_Op(instruction))
        self._take_snapshot(instruction)

    def _process_next_instruction(self, instruction: Knitout_Instruction | Knitout_Comment_Line) -> None:
        """
        Args:
            instruction (Knitout_Instruction | Knitout_Comment_Line): The instruction or comment to execute and update the current executer state.
        """
        try:
            if isinstance(instruction, (Pause_Instruction, Knitout_Comment_Line)):
                self._add_non_executable_instruction_to_execution(instruction)
            elif isinstance(instruction, Needle_Instruction):
                if not isinstance(instruction, (Xfer_Instruction, Split_Instruction, Drop_Instruction, Knit_Pass_Instruction, Miss_Instruction)):
                    raise TypeError(f"Found Needle_Instruction {instruction} that cannot be added to any type of carriage pass.")
                if self._current_carriage_pass is None:  # Make a new Carriage Pass from this
                    self._current_carriage_pass = carriage_pass_typed_to_first_instruction(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                else:  # Check if instruction can be added to the carriage pass, add it or create a new current carriage pass
                    was_added = self._current_carriage_pass.add_instruction(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                    if not was_added:
                        self._execute_current_carriage_pass(next_cp_instruction=instruction)
            elif instruction.will_update_machine_state(self.knitting_machine):
                self._execute_current_carriage_pass()
                self._execute_and_add_instruction(instruction)
        except Knitout_Machine_StateError as e:
            raise e from None

    def _end_program(self) -> None:
        """
        Concludes execution of the given knitout program.
        * Cleans up any active carriage pass.
        * Updates the carriage_passes and left-most right-most needle data.
        """
        if self._current_carriage_pass is not None:
            self._execute_current_carriage_pass()

    def __len__(self) -> int:
        """
        Returns:
            int: The length of the executed knitout program, including headers, comments, and executed instructions.
        """
        return self.execution_length


def execute_knitout(
    knitout_program: Sequence[Knitout_Line] | str,
    knitting_machine: Knitout_Knitting_Machine[Knitout_LoopT] | Knitout_Machine_Specification | None = None,
    knitout_version: int = 2,
    debugger: Knitout_Debugger | None = None,
    write_to_file: str | None = None,
    relax_violations: bool | Iterable[Violation] = False,
) -> tuple[Knitout_Program, Knitting_Machine, Knit_Graph]:
    """
    Executes, verifies, and organizes the given knitout program and optionally writes it to a file.

    Args:
        knitout_program (Sequence[Knitout_Line] | str): The knitout program to be executed. If a string is provided, it will be interpreted as a file to read knitout from.
        knitting_machine (Knitting_Machine | Knitting_Machine_Specification, optional):
            The knitting machine to execute the program in.
            If a specification is provided, a new machine is created from the specification.
            Defaults to a new standard knitting machine.
        knitout_version (int, optional): The knitout version to execute in and write out. Defaults to 2.
        debugger (Knitout_Debugger, optional): An optional debugger to attach to the knitout process. Defaults to no debugger.
        write_to_file (str, optional): The name of the file to write knitout instructions to. Defaults to not writing a knitout file.
        relax_violations (bool | Iterable[Violation], optional): If True, all violations are relaxed. If violations are given, those violations are relaxed. Defaults to False (full validation).

    Returns:
        tuple[Knitout_Program, Knitting_Machine, Knit_Graph]:
            A Tuple containing the following:
            * The verified and organized knitout program
            * The knitting machine after completion of the process.
            * The knitgraph graph after completion of the process.
    """
    executer: Knitout_Executer[Knitout_LoopT] = Knitout_Executer(knitout_program, knitting_machine, debugger=debugger, relax_violations=relax_violations, knitout_version=knitout_version)

    if write_to_file is not None:
        executer.write_executed_instructions(write_to_file)
    return executer.executed_instructions, executer.knitting_machine, executer.resulting_knit_graph
