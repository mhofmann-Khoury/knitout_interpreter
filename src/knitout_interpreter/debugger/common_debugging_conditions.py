"""A library of common conditions for debugging steps and carriage-pass steps."""

from collections.abc import Iterable

from knitout_interpreter.debugger.knitout_debugger import Knitout_Debugger
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Comment_Line, Knitout_Line


def is_instruction_type(_debugger: Knitout_Debugger, instruction: Knitout_Comment_Line | Knitout_Instruction, instruction_type: type[Knitout_Line] | Iterable[type[Knitout_Line]]) -> bool:
    """
    Args:
        _debugger (Knitout_Debugger): The debugger calling the function.
        instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction that will execute next.
        instruction_type (type[Knitout_Line] | Iterable[type[Knitout_Line]]): One or more types of instructions to compare to.

    Returns:
        bool: True if the next instruction is of the given instruction type(s) or one of their subclasses update the machine state of the process being debugged.
    """
    return isinstance(instruction, instruction_type) if isinstance(instruction_type, type) else any(isinstance(instruction, t) for t in instruction_type)


def is_not_instruction_type(_debugger: Knitout_Debugger, instruction: Knitout_Comment_Line | Knitout_Instruction, instruction_type: type[Knitout_Line] | Iterable[type[Knitout_Line]]) -> bool:
    """
    Args:
        _debugger (Knitout_Debugger): The debugger calling the function.
        instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction that will execute next.
        instruction_type (type[Knitout_Line] | Iterable[type[Knitout_Line]]): One or more types of instructions to compare to.

    Returns:
        bool: True if the next instruction not the given instruction type(s) or one of their subclasses update the machine state of the process being debugged.
    """
    return not is_instruction_type(_debugger, instruction, instruction_type)


def not_comment(_debugger: Knitout_Debugger, instruction: Knitout_Comment_Line | Knitout_Instruction) -> bool:
    """
    Args:
        _debugger (Knitout_Debugger): The debugger calling the function.
        instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction that will execute next.

    Returns:
        bool: True if the next instruction is an instruction (not a comment).
    """
    return is_not_instruction_type(_debugger, instruction, Knitout_Comment_Line)


def will_update_machine_state(debugger: Knitout_Debugger, instruction: Knitout_Comment_Line | Knitout_Instruction) -> bool:
    """
    Args:
        debugger (Knitout_Debugger): The debugger calling the function.
        instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction that will execute next.

    Returns:
        bool: True if the next instruction will update the machine state of the process being debugged.
    """
    return instruction.will_update_machine_state(debugger.knitting_machine) if not isinstance(instruction, Knitout_Comment_Line) and debugger.knitting_machine is not None else False


def loop_count_is(debugger: Knitout_Debugger, _instruction: Knitout_Comment_Line | Knitout_Instruction, loop_count: int) -> bool:
    """
    Args:
        debugger (Knitout_Debugger): The debugger calling the function.
        _instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction that will execute next.
        loop_count (int): The target count of loops in the knitgraph rendered by the debugged process.

    Returns:
        bool: True debugged process has produced exactly loop_count loops.
    """
    return debugger.knitting_machine.knit_graph.last_loop.loop_id == loop_count if debugger.knitting_machine is not None and debugger.knitting_machine.knit_graph.last_loop is not None else False


def loop_count_exceeds(debugger: Knitout_Debugger, _instruction: Knitout_Comment_Line | Knitout_Instruction, loop_count: int) -> bool:
    """
    Args:
        debugger (Knitout_Debugger): The debugger calling the function.
        _instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction that will execute next.
        loop_count (int): The target count of loops in the knitgraph rendered by the debugged process.

    Returns:
        bool: True debugged process has produced more than loop_count loops.
    """
    return debugger.knitting_machine.knit_graph.last_loop.loop_id > loop_count if debugger.knitting_machine is not None and debugger.knitting_machine.knit_graph.last_loop is not None else False


def loop_count_less_than(debugger: Knitout_Debugger, _instruction: Knitout_Comment_Line | Knitout_Instruction, loop_count: int) -> bool:
    """
    Args:
        debugger (Knitout_Debugger): The debugger calling the function.
        _instruction (Knitout_Comment_Line | Knitout_Instruction): The instruction that will execute next.
        loop_count (int): The target count of loops in the knitgraph rendered by the debugged process.

    Returns:
        bool: True debugged process has produced less than loop_count loops.
    """
    return debugger.knitting_machine.knit_graph.last_loop.loop_id < loop_count if debugger.knitting_machine is not None and debugger.knitting_machine.knit_graph.last_loop is not None else False
