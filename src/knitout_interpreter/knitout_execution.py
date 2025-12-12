"""Module containing the knitout executer class"""

from collections.abc import Sequence
from typing import cast

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_errors.Knitout_Error import Knitout_Machine_StateError
from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.Header_Line import Knitout_Version_Line, Knitting_Machine_Header
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line, Knitout_Line, Knitout_No_Op
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction


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
        accepted_error_types: list | None = None,
        knitout_version: int = 2,
    ):
        """Initialize the knitout executer.

        Args:
            instructions (Sequence[Knitout_Line]): The knitout lines to execute.
            knitting_machine (Knitting_Machine, optional): The virtual knitting machine to execute instructions on. Defaults to the default Knitting Machine with no prior operations.
            accepted_error_types (Sequence[Type[Exception] | Exception], optional): List of exception types that can be resolved by commenting them out. Defaults to no exceptions.
            knitout_version (int, optional): The knitout version to use. Defaults to 2.
        """
        self._knitout_version = knitout_version
        if accepted_error_types is None:
            accepted_error_types = []
        if knitting_machine is None:
            knitting_machine = Knitting_Machine()
        self.knitting_machine: Knitting_Machine = knitting_machine
        self.executed_header: Knitting_Machine_Header = Knitting_Machine_Header(self.knitting_machine.machine_specification)
        self.executed_header.extract_header(instructions)
        self.instructions: list[Knitout_Instruction | Knitout_Comment_Line] = [i for i in instructions if isinstance(i, (Knitout_Instruction, Knitout_Comment_Line))]
        self.process: list[Knitout_Instruction | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Line] = []
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

    def test_and_organize_instructions(self, accepted_error_types: type[BaseException] | Sequence[type[BaseException]] | None = None) -> None:
        """Test the given execution and organize the instructions in the class structure.

        This method processes all instructions, organizing them into carriage passes and handling any errors that occur during execution.

        Args:
            accepted_error_types (type[BaseException] | Sequence[type[BaseException]], optional):
                A sequence of exceptions that instructions may throw that can be resolved by commenting them out.
                Defaults to not accepting any exceptions.
        """
        if accepted_error_types is None:
            exception_tuple: tuple[type[BaseException], ...] = ()
        elif isinstance(accepted_error_types, type) and issubclass(accepted_error_types, BaseException):
            # Single exception type -> convert to tuple
            exception_tuple = (accepted_error_types,)
        else:
            # Already a tuple of exception types
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

    def write_executed_instructions(self, filename: str) -> None:
        """Write a file with the organized knitout instructions.

        Args:
            filename (str): The file path to write the executed instructions to.
        """
        with open(filename, "w") as file:
            file.writelines([str(instruction) for instruction in self.executed_instructions])
