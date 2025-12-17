"""Module containing the knitout executer class"""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import TYPE_CHECKING, cast

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction

from knitout_interpreter._warning_stack_level_helper import get_user_warning_stack_level_from_knitout_interpreter_package
from knitout_interpreter.knitout_debugger.debug_decorator import debug_knitout_carriage_pass, debug_knitout_instruction
from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.Header_Line import Knitout_Version_Line, Knitting_Machine_Header
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line, Knitout_Line, Knitout_No_Op
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction

if TYPE_CHECKING:
    from knitout_interpreter.knitout_debugger.knitout_debugger import Knitout_Debugger


class Knitout_Executer:
    """A class used to execute a set of knitout instructions on a virtual knitting machine.
    Attributes:
        knitting_machine (Knitting_Machine): Knitting Machine instance being executed on.
        instructions (list[Knitout_Line]): Instructions to execute.
        process (list[Knitout_Instruction | Carriage_Pass]): The ordered list of instructions and carriage passes executed in the knitting process.
        executed_header (Knitting_Machine_Header): The header that creates this knitting machine.
        executed_instructions (list[Knitout_Line]): The instructions that executed and updated the knitting machine state.
    """

    def __init__(
        self,
        instructions: Sequence[Knitout_Line],
        knitting_machine: Knitting_Machine | None = None,
        accepted_error_types: type[BaseException] | tuple[type[BaseException], ...] | None = None,
        knitout_version: int = 2,
        set_line_numbers: bool = True,
        debugger: Knitout_Debugger | None = None,
    ):
        """Initialize the knitout executer.

        Args:

            instructions (Sequence[Knitout_Line]): The knitout lines to execute.
            knitting_machine (Knitting_Machine, optional): The virtual knitting machine to execute instructions on. Defaults to the default Knitting Machine with no prior operations.
            accepted_error_types (type[BaseException] | tuple[type[BaseException], ...], optional):
                A tuple of one or more exception types that can be resolved by converting instructions to no-ops. Defaults to allowing no exceptions.
            knitout_version (int, optional): The knitout version to use. Defaults to 2.
            set_line_numbers (bool, optional): If True, the original line numbers are set for the given instructions to match the order they are provided in. Defaults to True.
            debugger (Knitout_Debugger, optional): The debugger to attach to this knitout execution process. Defaults to having no debugger.
        """
        if set_line_numbers:
            for i, instruction in enumerate(instructions):
                instruction.original_line_number = i + 1
        self.debugger: Knitout_Debugger | None = None
        if debugger is not None:
            self.attach_debugger(debugger)
        self._knitout_version = knitout_version
        if knitting_machine is None:
            knitting_machine = Knitting_Machine()
        self.knitting_machine: Knitting_Machine = knitting_machine
        self.executed_header: Knitting_Machine_Header = Knitting_Machine_Header(self.knitting_machine.machine_specification)
        self.executed_header.extract_header(instructions)
        self.instructions: list[Knitout_Instruction | Knitout_Comment_Line] = [i for i in instructions if isinstance(i, (Knitout_Instruction, Knitout_Comment_Line))]
        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Line] = []
        self._execution: list[Knitout_Instruction | Knitout_Comment_Line] = []
        self._current_carriage_pass: None | Carriage_Pass = None
        self._executing_current_carriage_pass: bool = False

        self.test_and_organize_instructions(accepted_error_types)
        self._carriage_passes: list[Carriage_Pass] = [cp for cp in self.process if isinstance(cp, Carriage_Pass)]
        self._left_most_position: int | None = None
        self._right_most_position: int | None = None
        for cp in self._carriage_passes:
            left, right = cp.carriage_pass_range()
            if self._left_most_position is None:
                self._left_most_position = left
            elif left is not None:
                self._left_most_position = min(self._left_most_position, left)
            if self._right_most_position is None:
                self._right_most_position = right
            elif right is not None:
                self._right_most_position = max(self._right_most_position, right)

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

    @property
    def executing_current_carriage_pass(self) -> bool:
        """
        Returns:
            bool: True if the executer is currently executing a fully formed carriage pass. False otherwise.
        """
        return self._executing_current_carriage_pass

    @debug_knitout_instruction
    def _execute_instruction_in_current_carriage_pass(self, instruction: Knitout_Instruction | Knitout_Comment_Line, no_op_if_no_update: bool = True) -> None:
        """
        Executes the given instruction related to the current carriage pass and adds it to the knitout execution process.

        Args:
            instruction (Knitout_Instruction): The instruction to execute.
            no_op_if_no_update (bool, optional): If true, operations that do not update the machine state are added as No-Op comments. Defaults to True.
        """
        if instruction.execute(self.knitting_machine):
            self._execution.append(instruction)
        elif no_op_if_no_update:
            self._execution.append(Knitout_No_Op(instruction))

    @debug_knitout_carriage_pass
    def _execute_current_carriage_pass(self, next_cp_instruction: Needle_Instruction | None = None) -> None:
        """Execute carriage pass with an implied racking operation on the given knitting machine.

        Args:
            next_cp_instruction (Knitout_Instruction | None, optional):
                The next instruction at the beginning of the carriage pass that will follow the current carriage pass. Defaults to no carriage pass instruction following this pass.

        Notes:
            Ordering xfers in a rightward ascending direction.
        """
        if self.current_carriage_pass is None:
            return
        self._executing_current_carriage_pass = True
        self._execute_instruction_in_current_carriage_pass(self.current_carriage_pass.rack_instruction(), no_op_if_no_update=False)
        if self.current_carriage_pass.xfer_pass:
            self.current_carriage_pass.direction = Carriage_Pass_Direction.Rightward  # default xfers to be in ascending order
        for instruction in self.current_carriage_pass:
            self._execute_instruction_in_current_carriage_pass(instruction, no_op_if_no_update=True)
        self.process.append(self.current_carriage_pass)
        if next_cp_instruction is not None:
            self._current_carriage_pass = Carriage_Pass(next_cp_instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
        else:
            self._current_carriage_pass = None
        self._executing_current_carriage_pass = False
        return

    @debug_knitout_instruction
    def execute_instruction(self, instruction: Knitout_Instruction | Knitout_Comment_Line, accepted_error_types: type[BaseException] | tuple[type[BaseException], ...] | None) -> None:
        """
        Args:
            instruction (Knitout_Instruction | Knitout_Comment_Line): The instruction or comment to execute and update the current executer state.
            accepted_error_types (type[BaseException] | tuple[type[BaseException], ...] | None):
                A tuple of zero or more types of exceptions to allow during execution by converting to no-op instructions.
        """
        if accepted_error_types is None:
            error_tuple: type[BaseException] | tuple[type[BaseException], ...] = ()
        elif isinstance(accepted_error_types, type) and issubclass(accepted_error_types, BaseException):
            error_tuple: type[BaseException] | tuple[type[BaseException], ...] = (accepted_error_types,)
        else:
            error_tuple: type[BaseException] | tuple[type[BaseException], ...] = accepted_error_types
        try:
            if isinstance(instruction, (Pause_Instruction, Knitout_Comment_Line)):
                self._execution.append(instruction)
            elif isinstance(instruction, Needle_Instruction):
                if self._current_carriage_pass is None:  # Make a new Carriage Pass from this
                    self._current_carriage_pass = Carriage_Pass(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                else:  # Check if instruction can be added to the carriage pass, add it or create a new current carriage pass
                    was_added = self._current_carriage_pass.add_instruction(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                    if not was_added:
                        self._execute_current_carriage_pass(next_cp_instruction=instruction)
            elif instruction.will_update_machine_state(self.knitting_machine):
                if self._current_carriage_pass is not None:
                    self._execute_current_carriage_pass()
                updated = instruction.execute(self.knitting_machine)
                assert updated, f"Expected {instruction} to update machine state"
                self.process.append(instruction)
                self._execution.append(instruction)
            else:  # Instruction will not update and should be converted to a No-OP comment
                no_op = Knitout_No_Op(instruction)
                self._execution.append(no_op)
        except error_tuple as e:
            no_op = Knitout_No_Op(instruction, f"Excluded {type(e).__name__}: {e.message}")
            self.executed_instructions.append(no_op)
        except Knitout_Machine_StateError as e:
            raise Knitout_Machine_StateError(instruction, e.error) from e

    def end_program(self) -> None:
        """
        Concludes execution of the given knitout program.
        * Cleans up any active carriage pass.
        * Updates the carriage_passes and left-most right-most needle data.
        """
        if self._current_carriage_pass is not None:
            self._execute_current_carriage_pass()
        # add the header and version line to the beginning of the executed instructions
        self.executed_instructions = cast(list[Knitout_Line], self.executed_header.get_header_lines(self.knitout_version))
        self.executed_instructions.extend(self._execution)
        self._carriage_passes: list[Carriage_Pass] = [cp for cp in self.process if isinstance(cp, Carriage_Pass)]
        self._left_most_position: int | None = None
        self._right_most_position: int | None = None
        for cp in self._carriage_passes:
            left, right = cp.carriage_pass_range()
            if self._left_most_position is None:
                self._left_most_position = left
            elif left is not None:
                self._left_most_position = min(self._left_most_position, left)
            if self._right_most_position is None:
                self._right_most_position = right
            elif right is not None:
                self._right_most_position = max(self._right_most_position, right)

    def test_and_organize_instructions(self, accepted_error_types: type[BaseException] | tuple[type[BaseException], ...] | None = None) -> None:
        """Test the given execution and organize the instructions in the class structure.

        This method processes all instructions, organizing them into carriage passes and handling any errors that occur during execution.

        Args:
            accepted_error_types (type[BaseException] | tuple[type[BaseException], ...], optional):
                One or more error types that should be accepted and have the invalid knitout instruction replaced with a no-op instruction.
                Defaults to not accepting any exceptions.
        """
        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self._execution: list[Knitout_Line] = []
        self._current_carriage_pass = None
        for _i, instruction in enumerate(self.instructions):
            self.execute_instruction(instruction, accepted_error_types)
        self.end_program()

    def dep_test_and_organize_instructions(self, accepted_error_types: type[BaseException] | Sequence[type[BaseException]] | None = None) -> None:
        """Test the given execution and organize the instructions in the class structure.

        This method processes all instructions, organizing them into carriage passes and handling any errors that occur during execution.

        Args:
            accepted_error_types (type[BaseException] | Sequence[type[BaseException]], optional):
                A sequence of exceptions that instructions may throw that can be resolved by commenting them out.
                Defaults to not accepting any exceptions.
        """
        warnings.warn(DeprecationWarning("Deprecating the old test_and_organize_instructions function"), stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package())
        if accepted_error_types is None:
            exception_tuple: tuple[type[BaseException], ...] = ()
        elif isinstance(accepted_error_types, type) and issubclass(accepted_error_types, BaseException):
            exception_tuple = (accepted_error_types,)
        else:
            exception_tuple = tuple(accepted_error_types)

        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Line] = []
        current_pass = None
        for instruction in self.instructions:
            try:
                if isinstance(instruction, (Pause_Instruction, Knitout_Comment_Line)):
                    self.executed_instructions.append(instruction)
                elif isinstance(instruction, Needle_Instruction):
                    if current_pass is None:  # Make a new Carriage Pass from this
                        current_pass = Carriage_Pass(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                    else:  # Check if instruction can be added to the carriage pass, add it or create a new current carriage pass
                        was_added = current_pass.add_instruction(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                        if not was_added:
                            self.executed_instructions.extend(current_pass.execute(self.knitting_machine))
                            self.process.append(current_pass)
                            current_pass = Carriage_Pass(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                elif instruction.will_update_machine_state(self.knitting_machine):
                    if current_pass is not None:
                        self.executed_instructions.extend(current_pass.execute(self.knitting_machine))
                        self.process.append(current_pass)
                        current_pass = None
                    updated = instruction.execute(self.knitting_machine)
                    assert updated, f"Expected {instruction} to update machine state"
                    self.process.append(instruction)
                    self.executed_instructions.append(instruction)
                else:
                    self.executed_instructions.append(Knitout_No_Op(instruction))
            except exception_tuple as e:
                comment = Knitout_No_Op(instruction, f"Excluded {type(e).__name__}: {e.message}")
                self.executed_instructions.append(comment)
            except Knitout_Machine_StateError as e:
                raise Knitout_Machine_StateError(instruction, e.error) from e
        if current_pass is not None:
            self.executed_instructions.extend(current_pass.execute(self.knitting_machine))
            self.process.append(current_pass)
        # add the header and version line to the beginning of the executed instructions
        executed_process = self.executed_instructions
        self.executed_instructions: list[Knitout_Line] = cast(list[Knitout_Line], self.executed_header.get_header_lines(self.knitout_version))
        self.executed_instructions.extend(executed_process)

    @property
    def knitout_version(self) -> int:
        """
        Returns:
            int: The knitout version being executed.
        """
        return self._knitout_version

    @property
    def version_line(self) -> Knitout_Version_Line:
        """Get the version line for the executed knitout.

        Returns:
            Knitout_Version_Line: The version line for the executed knitout.
        """
        return Knitout_Version_Line(self.knitout_version)

    @property
    def execution_time(self) -> int:
        """Get the execution time as measured by carriage passes.

        Returns:
            int: Count of carriage passes in process as a measure of knitting time.
        """
        return len(self._carriage_passes)

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
    def resulting_knit_graph(self) -> Knit_Graph:
        """Get the knit graph resulting from instruction execution.

        Returns:
            Knit_Graph: Knit Graph that results from execution of these instructions.
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
    def current_carriage_pass(self) -> None | Carriage_Pass:
        """
        Returns:
            None | Carriage_Pass: The carriage pass currently being formed in the knitout execution or None if no carriage pass is being formed.
        """
        return self._current_carriage_pass

    @property
    def executed_program(self) -> list[Knitout_Instruction | Knitout_Comment_Line]:
        """
        Returns:
            list[Knitout_Instruction | Knitout_Comment_Line]: The knitout instructions and comments that have been executed so far.
        """
        return self._execution

    @property
    def execution_length(self) -> int:
        """
        Returns:
            int: The number of lines in the completed execution. This includes the lines for the header, all comments, and all executed instructions.
        """
        execution_to_current_pass = self.executed_header.header_len + len(self._execution)
        if self.current_carriage_pass is None:
            return execution_to_current_pass
        else:
            return execution_to_current_pass + len(self.current_carriage_pass)

    def write_executed_instructions(self, filename: str) -> None:
        """Write a file with the organized knitout instructions.

        Args:
            filename (str): The file path to write the executed instructions to.
        """
        with open(filename, "w") as file:
            file.writelines([str(instruction) for instruction in self.executed_instructions])
