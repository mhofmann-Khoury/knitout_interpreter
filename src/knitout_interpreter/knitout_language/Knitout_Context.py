"""Module used to manage the context of a knitout interpreter."""
from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.Header_Line import Knitout_Header_Line
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line, Knitout_Version_Line, Knitout_Comment_Line
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction


def process_knitout_instructions(codes: list[Knitout_Line]) -> (
        tuple)[Knitout_Version_Line, list[Knitout_Header_Line], list[Knitout_Instruction], list[Knitout_Comment_Line]]:
    """
    Separate list of knitout codes into components of a program for execution.
    :param codes: List of knitout instructions to separate into program components
    :return: Version, header, separated instructions, separated comments
    """
    version: Knitout_Version_Line = Knitout_Version_Line(-1)  # -1 set to undo default if no version line is provided.
    head: list[Knitout_Header_Line] = []
    instructions: list[Knitout_Instruction] = []
    comments: list[Knitout_Comment_Line] = []
    for code in codes:
        if isinstance(code, Knitout_Version_Line):
            assert version == code.version or version.version < 0, f"Cannot have multiple versions of knitout {version} and {code}"
            version = code
        elif isinstance(code, Knitout_Header_Line):
            head.append(code)
        elif isinstance(code, Knitout_Instruction):
            instructions.append(code)
        elif isinstance(code, Knitout_Comment_Line):
            comments.append(code)
        else:
            assert False, f"Cannot process code {code}"
    if version.version < 0:
        version = Knitout_Version_Line(2, "Version defaulted to 2")
    return version, head, instructions, comments


class Knitout_Context:
    """Maintains information about hte state of a knitting process as knitout instructions are executed."""
    def __init__(self):
        self.machine_state: Knitting_Machine = Knitting_Machine()
        self.executed_knitout: list[Knitout_Line] = []
        self.version_line: Knitout_Version_Line | None = None
        self.executed_header: list[Knitout_Header_Line] = []
        self.executed_instructions: list[Knitout_Instruction] = []

    @property
    def version(self) -> int:
        """
        :return: Knitout version of the current context
        """
        if self.version_line is not None:
            return self.version_line.version
        else:
            return 2

    def add_version(self, version_line: Knitout_Version_Line):
        """
        Adds the given version line to the current context.
        Overrides the existing version.
        :param version_line:
        """
        self.version_line = version_line

    def execute_header(self, header_declarations: list[Knitout_Header_Line]):
        """
        Updates the machine state by the given header values.
        If header declarations do not change the current context, they are converted to comments.
        :param header_declarations: The header lines to update based on.
        """
        for header_line in header_declarations:
            updated = header_line.execute(self.machine_state)
            if not updated:
                self.executed_knitout.append(Knitout_Comment_Line(header_line))
            else:
                self.executed_knitout.append(header_line)
                self.executed_header.append(header_line)

    def execute_instructions(self, instructions: list[Knitout_Line]):
        """
        Executes the instruction set on the machine state defined by the current header.
        :param instructions: Instructions to execute on knitting machine.
        """
        execution = Knitout_Executer(instructions, self.machine_state)
        self.executed_instructions = execution.executed_instructions

    def execute_knitout(self, version_line: Knitout_Version_Line,
                        header_declarations: list[Knitout_Header_Line],
                        instructions: list[Knitout_Instruction]) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
        """
        Executes the given knitout organized by version, header, and instructions.
        :param version_line: The Version of knitout to use
        :param header_declarations: The header to define the knitout file.
        :param instructions: The instructions to execute on the machine.
        :return: The machine state after execution, the knit graph created by execution.
        """
        self.add_version(version_line)
        self.execute_header(header_declarations)
        self.execute_instructions(instructions)
        execution: list[Knitout_Line] = self.executed_header
        execution.extend(self.executed_instructions)
        for i, instruction in enumerate(execution):
            instruction.original_line_number = i
        return execution, self.machine_state, self.machine_state.knit_graph

    def process_knitout_file(self, knitout_file_name: str) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
        """
        Parse and process a file of knitout code.
        :param knitout_file_name: File with Knitout to process.
        :return: Knitting machine state after execution. Knit Graph formed by execution.
        """
        codes = parse_knitout(knitout_file_name, pattern_is_file=True, debug_parser=False, debug_parser_layout=False)
        return self.execute_knitout_instructions(codes)

    def execute_knitout_instructions(self, codes: list[Knitout_Line]) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
        """
        Execute given knitout instructions.
        :param codes: List of knitout lines to execute
        :return: The machine state after execution, the knit graph created by execution.
        """
        version, head, instructions, comments = process_knitout_instructions(codes)
        return self.execute_knitout(version, head, instructions)
