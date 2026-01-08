"""Factory function for building knitout instructions based on instruction type."""

from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import Yarn_Carrier_Set

from knitout_interpreter.knitout_operations.carrier_instructions import In_Instruction, Inhook_Instruction, Out_Instruction, Outhook_Instruction, Releasehook_Instruction, Yarn_Carrier_Instruction
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction, Knitout_Instruction_Type
from knitout_interpreter.knitout_operations.needle_instructions import Drop_Instruction, Knit_Instruction, Miss_Instruction, Needle_Instruction, Split_Instruction, Tuck_Instruction, Xfer_Instruction
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction


def build_two_needle_instruction(
    instruction_type: Knitout_Instruction_Type,
    first_needle: Needle,
    second_needle: Needle,
    direction: None | Carriage_Pass_Direction = None,
    carrier_set: Yarn_Carrier_Set | None = None,
    comment: str | None = None,
) -> Xfer_Instruction | Split_Instruction:
    """
    Builds a knitout instruction based on the specified instruction type and parameters.

    This factory function creates the appropriate two needle instruction (xfer or split) based on the instruction type and provided parameters.

    Args:
        instruction_type (Knitout_Instruction_Type): The type of knitout instruction to create. Must be a Xfer or Split
        first_needle (Needle): The primary needle for the operation.
        second_needle (Needle): The secondary needle loops are transferred to.
        direction (Carriage_Pass_Direction, optional): The carriage pass direction for directed split operations.
        carrier_set (Yarn_Carrier_Set, optional): The carrier set to use for split operations
        comment (str | None, optional): Optional comment to include with the instruction for documentation or debugging purposes.

    Returns:
        Xfer_Instruction | Split_Instruction: The constructed xfer or split corresponding to the specified type.

    Raises:
        ValueError: If a split instruction is not provided the direction or carrier values.
    """
    if instruction_type is Knitout_Instruction_Type.Xfer:
        return Xfer_Instruction(first_needle, second_needle, comment=comment)
    else:  # Split
        if direction is None:
            raise ValueError(f"{instruction_type.name} instructions require a direction")
        if carrier_set is None:
            raise ValueError(f"{instruction_type.name} instructions require a carrier set")
        return Split_Instruction(first_needle, direction, second_needle, carrier_set, comment)


def build_directed_needle_instruction(
    instruction_type: Knitout_Instruction_Type,
    first_needle: Needle,
    direction: Carriage_Pass_Direction,
    carrier_set: Yarn_Carrier_Set,
    comment: str | None = None,
) -> Knit_Instruction | Tuck_Instruction | Miss_Instruction | Kick_Instruction:
    """Builds knitout instructions that operate on one needle in a directed carriage pass (e.g., miss, knit, tuck).

    Args:
        instruction_type (Knitout_Instruction_Type): The type of knitout instruction to create.
        first_needle (Needle): The needle for the operation.
        direction (Carriage_Pass_Direction): The carriage pass direction.
        carrier_set (Yarn_Carrier_Set): The carrier set to use for the operation.
        comment (str, optional): Optional comment to include with the instruction for documentation or debugging purposes. Defaults to no comment.

    Returns:
        Knit_Instruction | Tuck_Instruction | Miss_Instruction | Kick_Instruction: The constructed knitout instruction object corresponding to the specified type.
    """
    if instruction_type is Knitout_Instruction_Type.Knit:
        return Knit_Instruction(first_needle, direction, carrier_set, comment=comment)
    elif instruction_type is Knitout_Instruction_Type.Tuck:
        return Tuck_Instruction(first_needle, direction, carrier_set, comment=comment)
    elif instruction_type is Knitout_Instruction_Type.Miss:
        return Miss_Instruction(first_needle, direction, carrier_set, comment)
    else:
        return Kick_Instruction(first_needle, direction, carrier_set, comment)


def build_needle_instruction(
    instruction_type: Knitout_Instruction_Type,
    first_needle: Needle,
    direction: Carriage_Pass_Direction | None = None,
    carrier_set: Yarn_Carrier_Set | None = None,
    second_needle: Needle | None = None,
    comment: str | None = None,
) -> Needle_Instruction:
    """Builds a knitout instruction that operates on a needle.

    Args:
        instruction_type (Knitout_Instruction_Type): The type of knitout instruction to create.
        first_needle (Needle): The primary needle for the operation.
        direction (Carriage_Pass_Direction, optional): The carriage pass direction for directional operations. Required for operations that involve yarn carrier movement.
        carrier_set (Yarn_Carrier_Set , optional): The carrier set to use for the operation. Required for operations that manipulate yarn.
        second_needle (Needle, optional): The secondary needle for operations requiring two needles, such as  transfers and splits.
        comment (str | None, optional): Optional comment to include with the instruction for documentation or debugging purposes.

    Returns:
        Needle_Instruction: The constructed knitout instruction object corresponding to the specified type.

    Raises:
        ValueError: If the instruction is not provided the appropriate values
    """
    if instruction_type.requires_second_needle:  # Xfer or Split
        if second_needle is None:
            raise ValueError(f"{instruction_type.name} instructions require a Second Needle.")
        return build_two_needle_instruction(instruction_type, first_needle, second_needle, direction, carrier_set, comment)
    elif instruction_type.directed_pass:  # Loop making or miss
        if carrier_set is None:
            raise ValueError(f"{instruction_type.name} instructions require a carrier set")
        if direction is None:
            raise ValueError(f"{instruction_type.name} instructions require a direction")
        return build_directed_needle_instruction(instruction_type, first_needle, direction, carrier_set, comment)
    else:  # Drop
        return Drop_Instruction(first_needle, comment=comment)


def build_carrier_instruction(instruction_type: Knitout_Instruction_Type, carrier_set: Yarn_Carrier, comment: str | None = None) -> Yarn_Carrier_Instruction:
    """
    Args:
        instruction_type (Knitout_Instruction_Type): The type of knitout instruction to create. Assumed to be a carrier instruction.
        carrier_set (Yarn_Carrier): The yarn-carrier to use for the operation.
        comment (str | None, optional): Optional comment to include with the instruction for documentation or debugging purposes.

    Returns:
        Yarn_Carrier_Instruction: The carrier instruction constructed from the given specification.
    """
    if instruction_type is Knitout_Instruction_Type.Outhook:
        return Outhook_Instruction(carrier_set, comment)
    elif instruction_type is Knitout_Instruction_Type.Out:
        return Out_Instruction(carrier_set, comment)
    elif instruction_type is Knitout_Instruction_Type.In:
        return In_Instruction(carrier_set, comment)
    elif instruction_type is Knitout_Instruction_Type.Inhook:
        return Inhook_Instruction(carrier_set, comment)
    else:  # Releasehook
        return Releasehook_Instruction(carrier_set, comment)


def build_instruction(
    instruction_type: Knitout_Instruction_Type,
    first_needle: Needle | None = None,
    direction: None | Carriage_Pass_Direction = None,
    carrier_set: Yarn_Carrier_Set | Yarn_Carrier | None = None,
    second_needle: Needle | None = None,
    racking: float | None = None,
    comment: str | None = None,
) -> Knitout_Instruction:
    """Builds a knitout instruction based on the specified instruction type and parameters.

    This factory function creates the appropriate knitout instruction object based on the instruction type and provided parameters.
    It handles all supported knitout instruction types including needle operations, carrier operations, and machine control operations.

    Args:
        instruction_type (Knitout_Instruction_Type): The type of knitout instruction to create.
        first_needle (Needle, optional): The primary needle for the operation. Required for needle-based instructions like knit, tuck, drop, etc.
        direction (Carriage_Pass_Direction, optional): The carriage pass direction for directional operations. Required for operations that involve yarn carrier movement.
        carrier_set (Yarn_Carrier_Set | Yarn_Carrier, optional): The yarn carrier or carrier set to use for the operation. Required for operations that manipulate yarn.
        second_needle (Needle, optional): The secondary needle for operations requiring two needles, such as  transfers and splits.
        racking (float, optional): The racking value for rack instructions. Specifies the relative position between needle beds.
        comment (str | None, optional): Optional comment to include with the instruction for documentation or debugging purposes.

    Returns:
        Knitout_Instruction: The constructed knitout instruction object corresponding to the specified type.

    Raises:
        ValueError: If the instruction is not provided the appropriate values
    """
    if instruction_type.is_needle_instruction:
        if first_needle is None:
            raise ValueError(f"{instruction_type.name} instructions require a Needle.")
        if isinstance(carrier_set, Yarn_Carrier):
            carrier_set = Yarn_Carrier_Set(carrier_set)  # convert a carrier to a carrier set to be passed to needle operations.
        return build_needle_instruction(instruction_type, first_needle, direction, carrier_set, second_needle, comment)
    elif instruction_type.is_carrier_instruction:
        if not isinstance(carrier_set, Yarn_Carrier):
            raise ValueError(f"{instruction_type.name} instructions require a carrier")
        return build_carrier_instruction(instruction_type, carrier_set, comment)
    elif instruction_type is Knitout_Instruction_Type.Rack:
        if racking is None:
            raise ValueError(f"{instruction_type.name} instructions require a rack value")
        return Rack_Instruction(racking, comment)
    else:  # Pause
        return Pause_Instruction(comment)
