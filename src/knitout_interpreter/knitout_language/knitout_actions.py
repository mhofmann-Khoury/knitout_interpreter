"""Actions for reducing in Knitout Parser"""

from collections.abc import Callable
from typing import Any, TypeVar, cast

from parglare import get_collector
from parglare.parser import LRStackNode
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle_Position, Needle_Specification
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_operations.carrier_instructions import In_Instruction, Inhook_Instruction, Out_Instruction, Outhook_Instruction, Releasehook_Instruction
from knitout_interpreter.knitout_operations.Header_Line import Carriers_Header_Line, Gauge_Header_Line, Knitout_Header_Line, Knitout_Version_Line, Machine_Header_Line, Position_Header_Line
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_BreakPoint, Knitout_Comment_Line, Knitout_Line, Knitout_No_Op
from knitout_interpreter.knitout_operations.needle_instructions import Drop_Instruction, Kick_Instruction, Knit_Instruction, Miss_Instruction, Split_Instruction, Tuck_Instruction, Xfer_Instruction
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction

action = get_collector()

F = TypeVar("F", bound=Callable[..., Any])


def typed_action(func: F) -> F:
    """
    Wrapper that applies @action decorator while preserving types.

    Args:
        func (F): Function to be decorated with the action decorator.

    Returns:
        F: Wrapped function.
    """
    return cast(F, action(func))


@typed_action
def no_op(_: LRStackNode, __: list, value: Knitout_Instruction, com: str | None) -> Knitout_Comment_Line:
    """Extracts the content of a no op comment

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        value (Knitout_Instruction): The no-op commented instruction.
        com (str | None): Additional comment to the instruction

    Returns:
        Knitout_Comment_Line: The No-op comment for the given instruction.
    """
    return Knitout_No_Op(value, additional_comment=com)


@typed_action
def break_point(_: LRStackNode, __: list, content: str | None) -> Knitout_BreakPoint:
    """Extracts the content of a break point with a comment.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        content (str | None): The content of the comment of the breakpoint.

    Returns:
        Knitout_BreakPoint: The breakpoint.
    """
    return Knitout_BreakPoint(content)


@typed_action
def comment(_: LRStackNode, __: list, content: str | None) -> str | None:
    """Extracts the content of a comment.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        content (str | None): The content of the comment.

    Returns:
        str | None: The content of the comment.
    """
    return content


@typed_action
def comment_line(_: LRStackNode, __: list, content: str) -> Knitout_Comment_Line:
    """Extracts the content of a comment.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        content (str): The content of the comment.

    Returns:
        Knitout_Comment_Line: The comment line.
    """
    return Knitout_Comment_Line(content)


@typed_action
def code_line(_: LRStackNode, __: list, c: Knitout_Line | None, com: str | None) -> Knitout_Line | None:
    """Creates a knitout line with optional comment.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        c (Knitout_Line | None): The knitout line to execute, if any.
        com (str | None): The comment to append to the knitout line.

    Returns:
        Knitout_Line | None: The knitout line created or None if no values are given.
    """
    if c is None:
        if com is None:
            return None
        c = Knitout_Comment_Line(comment=com)
    if com is not None:
        if c.comment is not None:
            c.comment += com
        else:
            c.comment = com
    return c


@typed_action
def magic_string(_: LRStackNode, __: list, v: int) -> Knitout_Version_Line:
    """Creates a knitout version line.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        v (int): Version number.

    Returns:
        Knitout_Version_Line: The version line knitout line.
    """
    return Knitout_Version_Line(v)


@typed_action
def header_line(_: LRStackNode, __: list, h_op: Knitout_Header_Line) -> Knitout_Header_Line:
    """Returns a header line operation.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        h_op (Knitout_Header_Line): Operation on the line.

    Returns:
        Knitout_Header_Line: The header operation.
    """
    return h_op


@typed_action
def machine_op(_: LRStackNode, __: list, m: str) -> Machine_Header_Line:
    """Creates a machine header line.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        m (str): The machine name as a string.

    Returns:
        Machine_Header_Line: The machine declaration operation.
    """
    return Machine_Header_Line(m)


@typed_action
def gauge_op(_: LRStackNode, __: list, g: int) -> Gauge_Header_Line:
    """Creates a gauge header line.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        g (int): Gauge value.

    Returns:
        Gauge_Header_Line: The gauge header.
    """
    return Gauge_Header_Line(g)


@typed_action
def yarn_op(_: LRStackNode, __: list, cid: int, color: str) -> Knitout_Comment_Line:
    """Creates a yarn header line.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        cid: The carrier to assign the yarn too.
        color: The yarn color.

    Returns:
        Comment of yarn declaration.
    """
    return Knitout_Comment_Line(f"Yarn-{cid}-{color}")


@typed_action
def carriers_op(_: LRStackNode, __: list, CS: Yarn_Carrier_Set) -> Carriers_Header_Line:
    """Creates a carriers header line.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        CS: The carriers that are available.

    Returns:
        Carrier declaration.
    """
    return Carriers_Header_Line(CS)


@typed_action
def position_op(_: LRStackNode, __: list, p: str) -> Position_Header_Line:
    """Creates a position header line.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        p: The position of operations.

    Returns:
        The position declaration.
    """
    return Position_Header_Line(p)


@typed_action
def in_op(_: LRStackNode, __: list, c: int) -> In_Instruction:
    """Creates an in instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        c: The carrier to bring in.

    Returns:
        In operation on a carrier set.
    """
    return In_Instruction(c)


@typed_action
def inhook_op(_: LRStackNode, __: list, c: int) -> Inhook_Instruction:
    """Creates an inhook instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        c: The carrier to hook in.

    Returns:
        Inhook operation on carrier set.
    """
    return Inhook_Instruction(c)


@typed_action
def releasehook_op(_: LRStackNode, __: list, c: int) -> Releasehook_Instruction:
    """Creates a releasehook instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        c: Carrier set.

    Returns:
        Releasehook operation on carrier set.
    """
    return Releasehook_Instruction(c)


@typed_action
def out_op(_: LRStackNode, __: list, c: int) -> Out_Instruction:
    """Creates an out instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        c: Carrier set.

    Returns:
        Out operation on the carrier set.
    """
    return Out_Instruction(c)


@typed_action
def outhook_op(_: LRStackNode, __: list, c: int) -> Outhook_Instruction:
    """Creates an outhook instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        c: Carrier set.

    Returns:
        Outhook operation on the carrier set.
    """
    return Outhook_Instruction(c)


@typed_action
def rack_op(_: LRStackNode, __: list, R: float) -> Rack_Instruction:
    """Creates a rack instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        R: Rack value.

    Returns:
        Rack operation.
    """
    return Rack_Instruction(R)


@typed_action
def knit_op(_: LRStackNode, __: list, D: str, N: Needle_Specification, CS: Yarn_Carrier_Set) -> Knit_Instruction:
    """Creates a knit instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        D: Direction operates in.
        N: Needle to operate on.
        CS: A carrier set.

    Returns:
        Knit operation.
    """
    return Knit_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@typed_action
def tuck_op(_: LRStackNode, __: list, D: str, N: Needle_Specification, CS: Yarn_Carrier_Set) -> Tuck_Instruction:
    """Creates a tuck instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        D: Direction operates in.
        N: Needle to operate on.
        CS: A carrier set.

    Returns:
        Tuck operation.
    """
    return Tuck_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@typed_action
def miss_op(_: LRStackNode, __: list, D: str, N: Needle_Specification, CS: Yarn_Carrier_Set) -> Miss_Instruction:
    """Creates a miss instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        D: Direction to operate in.
        N: Needle to operate on.
        CS: A carrier set.

    Returns:
        Miss operation.
    """
    return Miss_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@typed_action
def kick_op(_: LRStackNode, __: list, D: str, N: Needle_Specification, CS: Yarn_Carrier_Set) -> Kick_Instruction:
    """Creates a kick instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        D: The direction to operate in.
        N: The needle to position the kickback.
        CS: The carrier set to kick.

    Returns:
        The specified Kick Operation.
    """
    return Kick_Instruction(N.position, Carriage_Pass_Direction.get_direction(D), CS)


@typed_action
def split_op(_: LRStackNode, __: list, D: str, N: Needle_Specification, N2: Needle_Specification, CS: Yarn_Carrier_Set) -> Split_Instruction:
    """Creates a split instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        D: Direction operates in.
        N: Needle to operate on.
        N2: Second needle to move to.
        CS: A carrier set.

    Returns:
        Split operation.
    """
    return Split_Instruction(N, Carriage_Pass_Direction.get_direction(D), N2, CS)


@typed_action
def drop_op(_: LRStackNode, __: list, N: Needle_Specification) -> Drop_Instruction:
    """Creates a drop instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        N: Needle to drop from.

    Returns:
        Drop operation.
    """
    return Drop_Instruction(N)


@typed_action
def xfer_op(_: LRStackNode, __: list, N: Needle_Specification, N2: Needle_Specification) -> Xfer_Instruction:
    """Creates a transfer instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        N: Needle to transfer from.
        N2: Needle to transfer to.

    Returns:
        Xfer operation.
    """
    return Xfer_Instruction(N, N2)


@typed_action
def pause_op(_: LRStackNode, __: list) -> Pause_Instruction:
    """Creates a pause instruction.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.

    Returns:
        Pause operation.
    """
    return Pause_Instruction()


@typed_action
def identifier(_: Any, node: str) -> str:
    """Returns an identifier string.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        node: Identifier string.

    Returns:
        The identifier string.
    """
    return node


@typed_action
def float_exp(_: Any, node: str) -> float:
    """Converts a string to a float.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        node: Float string.

    Returns:
        Float conversion.
    """
    digits = ""
    for c in node:
        if c.isdigit() or c == "." or c == "-":
            digits += c
    return float(digits)


@typed_action
def int_exp(_: Any, node: str) -> int:
    """Converts a string to an integer.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        node: Integer string.

    Returns:
        Integer conversion.
    """
    return int(float_exp(None, node))


@typed_action
def needle_id(_: Any, node: str) -> Needle_Specification:
    """Creates a needle from a string representation.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        node: String of the given needle.

    Returns:
        The Needle represented by this string.
    """
    is_front = "f" in node
    slider = "s" in node
    num_str = node[1:]  # cut bed off
    if slider:
        num_str = node[2:]  # cut slider off
    pos = int(num_str)
    return Needle_Position(is_front, pos, slider)


@typed_action
def carrier_set(_: LRStackNode, __: list, carriers: list[int]) -> Yarn_Carrier_Set:
    """Creates a yarn carrier set.

    Args:
        _ (LRStackNode): The stack node element being processed by this action.
        __ (list): A list of values found for this action.
        carriers: Carriers in set.

    Returns:
        Carrier set.
    """
    return Yarn_Carrier_Set(cast(list[int | Yarn_Carrier], carriers))
