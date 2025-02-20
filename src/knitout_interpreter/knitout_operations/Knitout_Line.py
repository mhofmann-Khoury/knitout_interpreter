"""Base class for Knitout Lines of code"""
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine


class Knitout_Line:
    """
        General class for lines of knitout
    """
    _Lines_Made = 0

    def __init__(self, comment: str | None, interrupts_carriage_pass=False):
        Knitout_Line._Lines_Made += 1
        self._creation_time = Knitout_Line._Lines_Made
        self.comment = comment
        self.original_line_number: int | None = None
        self.follow_comments: list[Knitout_Comment_Line] = []
        self._interrupts_carriage_pass: bool = interrupts_carriage_pass

    @property
    def interrupts_carriage_pass(self) -> bool:
        """
        :return: True if this type of carriage pass interrupts a carriage pass or False if it is only used for comments or setting information.
        """
        return self._interrupts_carriage_pass

    def add_follow_comment(self, comment_line):
        """
        Adds comment line to comments that follow this line
        :param comment_line:
        """
        self.follow_comments.append(comment_line)

    @property
    def has_comment(self) -> bool:
        """
        :return: True if comment is present
        """
        return self.comment is not None

    @property
    def comment_str(self) -> str:
        """
        :return: comment as a string
        """
        if not self.has_comment:
            return "\n"
        else:
            return f";{self.comment}\n"

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """
        Executes the instruction on the machine state.
        :param machine_state: The knitting machine state to update.
        :return: True if the process completes an update.
        """
        return False

    def __str__(self):
        return self.comment_str

    @property
    def injected(self) -> bool:
        """
        :return: True if instruction was marked as injected by a negative line number.
        """
        return self.original_line_number is not None and self.original_line_number < 0

    def id_str(self) -> str:
        """
        :return: string with original line number added if present
        """
        if self.original_line_number is not None:
            return f"{self.original_line_number}:{self}"[:-1]
        else:
            return str(self)[-1:]

    def __repr__(self):
        if self.original_line_number is not None:
            return self.id_str()
        else:
            return str(self)

    # def __eq__(self, other):
    #     return str(self) == str(other)

    def __lt__(self, other):
        if self.original_line_number is None:
            if other.original_line_number is None:
                return False
            else:
                return True
        else:
            return self.original_line_number < other.original_line_number

    def __hash__(self):
        return hash(self._creation_time)


class Knitout_Version_Line(Knitout_Line):

    def __init__(self, version: int = 2, comment: None | str = None):
        super().__init__(comment, interrupts_carriage_pass=False)
        self.version: int = version

    def __str__(self):
        return f";!knitout-{self.version}{self.comment_str}"


class Knitout_Comment_Line(Knitout_Line):
    def __init__(self, comment: None | str | Knitout_Line):
        if isinstance(comment, Knitout_Line):
            if isinstance(comment, Knitout_Comment_Line):
                comment = Knitout_Comment_Line.comment_str
            else:
                comment = f"No-Op:\t{comment}"
        super().__init__(comment, interrupts_carriage_pass=False)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        return True
