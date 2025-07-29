"""Actions for reducing in Knitout Parser"""
from typing import Any

from parglare import get_collector
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import Slider_Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_operations.Header_Line import Knitout_Header_Line, Machine_Header_Line, Gauge_Header_Line, Yarn_Header_Line, Carriers_Header_Line, Position_Header_Line
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line, Knitout_Comment_Line, Knitout_Version_Line
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction
from knitout_interpreter.knitout_operations.carrier_instructions import In_Instruction, Inhook_Instruction, Releasehook_Instruction, Out_Instruction, Outhook_Instruction
from knitout_interpreter.knitout_operations.needle_instructions import Knit_Instruction, Tuck_Instruction, Miss_Instruction, Split_Instruction, Drop_Instruction, Xfer_Instruction

action = get_collector()


@action
def comment(_: Any, __: Any, content: str | None) -> str | None:
    """

    :param _:
    :param __:
    :param content: the content of the comment.
    :return: the content of the comment.
    """
    return content


@action
def code_line(_: Any, __: Any, c: Knitout_Line | None, com: str | None) -> Knitout_Line | None:
    """
    :param _:
    :param __:
    :param c: the knitout line to execute, if any
    :param com: the comment to append to the knitout line
    :return: the knitout line created or None if no values are given
    """
    if c is None:
        if com is None:
            return None
        c = Knitout_Comment_Line(comment=com)
    if com is not None:
        c.comment = com
    return c


@action
def magic_string(_: Any, __: Any, v: int) -> Knitout_Version_Line:
    """
    :param _:  The parser element that created this value
    :param __:
    :param v: version number
    :return: The version line knitout line.
    """
    return Knitout_Version_Line(v)


@action
def header_line(_: Any, __: Any, h_op: Knitout_Header_Line) -> Knitout_Header_Line:
    """
    :param _: The parser element that created this value
    :param __:
    :param h_op: operation on the line
    :return: the header operation
    """
    return h_op


@action
def machine_op(_: Any, __: Any, m: str) -> Machine_Header_Line:
    """
    :param _: The parser element that created this value
    :param __:
    :param m: the machine name as a string
    :return: the machine declaration operation
    """
    return Machine_Header_Line(m)


@action
def gauge_op(_: Any, __: Any, g: int) -> Gauge_Header_Line:
    """
    :param _: The parser element that created this value
    :param __:
    :param g: gauge value
    :return: Gauge_Declaration
    """
    return Gauge_Header_Line(g)


@action
def yarn_op(_: Any, __: Any, cid: int, plies: int, weight: int, color: str) -> Yarn_Header_Line:
    """
    :param plies: plies in the yarn.
    :param weight: weight of the yarn.
    :param _: The parser element that created this value.
    :param __:
    :param cid: The carrier to assign the yarn too.
    :param color: The yarn color.
    :return: Yarn declaration.
    """
    return Yarn_Header_Line(cid, plies, weight, color)


@action
def carriers_op(_: Any, __: Any, CS: Yarn_Carrier_Set) -> Carriers_Header_Line:
    """
    :param _: The parser element that created this value.
    :param __:
    :param __:
    :param CS: the carriers that are available.
    :return: carrier declaration.
    """
    return Carriers_Header_Line(CS)


@action
def position_op(_: Any, __: Any, p: str) -> Position_Header_Line:
    """
    :param _: The parser element that created this value.
    :param __:
    :param p: the position of operations.
    :return: the position declaration.
    """
    return Position_Header_Line(p)


@action
def in_op(_: Any, __: Any, c: int) -> In_Instruction:
    """
    :param c: The carrier to bring in.
    :param _: The parser element that created this value.
    :param __:
    :return: In operation on a carrier set.
    """
    return In_Instruction(c)


@action
def inhook_op(_: Any, __: Any, c: int) -> Inhook_Instruction:
    """
    :param c:
    :param _: The parser element that created this value
    :param __:
    :return: Inhook operation on carrier set
    """
    return Inhook_Instruction(c)


@action
def releasehook_op(_: Any, __: Any, c: int) -> Releasehook_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param c: carrier set
    :return: releasehook operation on carrier set
    """
    return Releasehook_Instruction(c)


@action
def out_op(_: Any, __: Any, c: int) -> Out_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param c: carrier set
    :return: out operation on the carrier set
    """
    return Out_Instruction(c)


@action
def outhook_op(_: Any, __: Any, c: int) -> Outhook_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param c: carrier set
    :return: outhook operation on the carrier set
    """
    return Outhook_Instruction(c)


@action
def rack_op(_: Any, __: Any, R: float) -> Rack_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param R: rack value
    :return: rack operation
    """
    return Rack_Instruction(R)


@action
def knit_op(_: Any, __: Any, D: str, N: Needle, CS: Yarn_Carrier_Set) -> Knit_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param D: direction operates in
    :param N: needle to operate on
    :param CS: a carrier set
    :return: knit operation
    """
    return Knit_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@action
def tuck_op(_: Any, __: Any, D: str, N: Needle, CS: Yarn_Carrier_Set) -> Tuck_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param D: direction operates in
    :param N: needle to operate on
    :param CS: a carrier set
    :return: tuck operation
    """
    return Tuck_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@action
def miss_op(_: Any, __: Any, D: str, N: Needle, CS: Yarn_Carrier_Set) -> Miss_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param D: direction to operate in
    :param N: needle to operate on
    :param CS: a carrier set
    :return: miss operation
    """
    return Miss_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@action
def split_op(_: Any, __: Any, D: str, N: Needle, N2: Needle, CS: Yarn_Carrier_Set) -> Split_Instruction:
    """
    :param N2: second needle to move to.
    :param _: The parser element that created this value
    :param __:
    :param D: Direction operates in
    :param N: needle to operate on
    :param CS: a carrier set
    :return: knit operation
    """
    return Split_Instruction(N, Carriage_Pass_Direction.get_direction(D), N2, CS)


@action
def drop_op(_: Any, __: Any, N: Needle) -> Drop_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param N: needle to drop from
    :return: drop operation
    """
    return Drop_Instruction(N)


@action
def xfer_op(_: Any, __: Any, N: Needle, N2: Needle) -> Xfer_Instruction:
    """
    :param _: The parser element that created this value
    :param __:
    :param N: Needle to transfer from
    :param N2: needle to transfer to.
    :return: Xfer operation
    """
    return Xfer_Instruction(N, N2)


@action
def pause_op(_: Any, __: Any) -> Pause_Instruction:
    """
    :param _:
    :param __:
    :return: pause operation
    """
    return Pause_Instruction()


@action
def identifier(_: Any, node: str) -> str:
    """
    :param _:
    :param node: identifier string
    :return: node
    """
    return node


@action
def float_exp(_: Any, node: str) -> float:
    """
    :param _:
    :param node: float string
    :return: float conversion
    """
    digits = ""
    for c in node:
        if c.isdigit() or c == "." or c == "-":
            digits += c
    return float(digits)


@action
def int_exp(_: Any, node: str) -> int:
    """
    :param _:
    :param node: int string
    :return: int conversion
    """
    return int(float_exp(None, node))


@action
def needle_id(_:Any, node: str) -> Needle:
    is_front = "f" in node
    slider = "s" in node
    num_str = node[1:]  # cut bed off
    if slider:
        num_str = node[1:]  # cut slider off
    pos = int(num_str)
    if slider:
        return Slider_Needle(is_front, pos)
    else:
        return Needle(is_front, pos)


@action
def carrier_set(_: Any, __: Any, carriers: list[int]) -> Yarn_Carrier_Set:
    """
    :param _: The parser element that created this value
    :param __:
    :param carriers: Carriers in set.
    :return: Carrier set
    """
    return Yarn_Carrier_Set(carriers)
