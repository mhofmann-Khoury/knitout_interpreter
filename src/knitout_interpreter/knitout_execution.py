"""Module containing the knitout executer class"""
from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line, Knitout_Comment_Line
from knitout_interpreter.knitout_operations.needle_instructions import Needle_Instruction


class Knitout_Executer:
    """A class used to execute a set of knitout instructions on a virtual knitting machine."""
    def __init__(self, instructions: list[Knitout_Line], knitting_machine: Knitting_Machine):
        self.knitting_machine = knitting_machine
        self.instructions: list[Knitout_Line] = instructions
        self.process: list[Knitout_Line | Carriage_Pass] = []
        self.executed_header: list[Knitout_Line] = []
        self.executed_instructions: list[Knitout_Line] = []
        self.test_and_organize_instructions()
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
    def execution_time(self) -> int:
        """
        :return: Count of carriage passes in process as a measure of knitting time
        """
        return len(self._carriage_passes)

    @property
    def left_most_position(self) -> int | None:
        """
        :return: The position of the left most needle used in execution.
        """
        return self._left_most_position

    @property
    def right_most_position(self) -> int | None:
        """
        :return: The position of the right most needle used in the execution.
        """
        return self._right_most_position

    @property
    def resulting_knit_graph(self) -> Knit_Graph:
        """
        :return: Knit Graph that results from execution of these instructions.
        """
        return self.knitting_machine.knit_graph

    @property
    def carriage_passes(self) -> list[Carriage_Pass]:
        """
        :return: The carriage passes resulting from this execution in execution order.
        """
        return self._carriage_passes

    def test_and_organize_instructions(self, accepted_error_types: list | None = None):
        if accepted_error_types is None:
            accepted_error_types = []
        self.process: list[Knitout_Line | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Line] = []
        current_pass = None
        for instruction in self.instructions:
            try:
                if isinstance(instruction, Needle_Instruction):
                    if current_pass is None:
                        current_pass = Carriage_Pass(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                    else:
                        was_added = current_pass.add_instruction(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                        if not was_added:
                            executed_pass = current_pass.execute(self.knitting_machine)
                            self.process.append(current_pass)
                            self.executed_instructions.extend(executed_pass)
                            current_pass = Carriage_Pass(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                else:
                    if current_pass is not None:
                        executed_pass = current_pass.execute(self.knitting_machine)
                        self.process.append(current_pass)
                        self.executed_instructions.extend(executed_pass)
                        current_pass = None
                    updated = instruction.execute(self.knitting_machine)
                    if updated:
                        self.process.append(instruction)
                        self.executed_instructions.append(instruction)
                    else:
                        comment = Knitout_Comment_Line(instruction)
                        self.process.append(comment)
                        self.executed_instructions.append(comment)
            except tuple(accepted_error_types) as e:
                error_comment = Knitout_Comment_Line(f"Excluded {type(e).__name__}: {e.message}")
                self.process.append(error_comment)
                self.executed_instructions.append(error_comment)
                comment = Knitout_Comment_Line(instruction)
                self.process.append(comment)
                self.executed_instructions.append(comment)
        if current_pass is not None:
            executed_pass = current_pass.execute(self.knitting_machine)
            self.process.append(current_pass)
            self.executed_instructions.extend(executed_pass)

    def write_executed_instructions(self, filename: str):
        """
        Write a file with the knitout organized knitout instructions
        :param filename: the file to write out to.
        """
        with open(filename, "w") as file:
            file.writelines([str(instruction) for instruction in self.executed_instructions])
