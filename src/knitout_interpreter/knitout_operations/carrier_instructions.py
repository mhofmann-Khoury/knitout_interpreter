"""Knitout Operations that involve the yarn inserting system"""

from __future__ import annotations

import warnings

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_warnings.carrier_operation_warnings import Mismatched_Releasehook_Warning
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import Carriage_Pass_Direction
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import Yarn_Carrier
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import Machine_Knit_Yarn

from knitout_interpreter._warning_stack_level_helper import get_user_warning_stack_level_from_knitout_interpreter_package
from knitout_interpreter.knitout_operations.knitout_instruction import Knitout_Instruction, Knitout_Instruction_Type


class Yarn_Carrier_Instruction(Knitout_Instruction):
    """Super class of all instructions related to the yarn-insertion system."""

    def __init__(self, instruction_type: Knitout_Instruction_Type, carrier: int | Yarn_Carrier, comment: None | str = None) -> None:
        """
        Args:
            instruction_type (Knitout_Instruction_Type): The type of instruction to execute.
            carrier (int | Yarn_Carrier): The carrier or carrier id of the carrier involved in the operation.
            comment (str, optional): The comment of the instruction.:
        """
        super().__init__(instruction_type, comment)
        self._carrier: int | Yarn_Carrier = carrier

    @property
    def carrier(self) -> int | Yarn_Carrier:
        """
        Returns:
            int | Yarn_Carrier: The carrier of the instruction.
        """
        return self._carrier

    @property
    def carrier_id(self) -> int:
        """
        Returns:
            int: The id of the carrier of the instruction.
        """
        return int(self._carrier)

    def __str__(self) -> str:
        return f"{self.instruction_type} {self.carrier_id}{self.comment_str}"

    def get_yarn(self, machine: Knitting_Machine) -> Machine_Knit_Yarn:
        """Get the yarn on the specified carrier.

        Args:
            machine (Knitting_Machine): The knitting machine to get yarn from.

        Returns:
            Machine_Knit_Yarn: The yarn on the specified carrier on the given machine.
        """
        return self.get_carrier(machine).yarn

    def get_carrier(self, machine: Knitting_Machine) -> Yarn_Carrier:
        """Get the yarn carrier specified on the given machine.

        Args:
            machine (Knitting_Machine): The knitting machine to get the carrier from.

        Returns:
            Yarn_Carrier: The yarn carrier specified on the given machine.
        """
        return machine.carrier_system[self.carrier_id]


class Hook_Instruction(Yarn_Carrier_Instruction):
    """Super class of all carrier instructions that involve the yarn-inserting hook."""

    def __init__(
        self,
        instruction_type: Knitout_Instruction_Type,
        carrier: int | Yarn_Carrier,
        comment: None | str = None,
        requires_clear_inserting_hook: bool = True,
    ):
        super().__init__(instruction_type, carrier, comment)
        self._required_clear_inserting_hook = requires_clear_inserting_hook

    @property
    def requires_clear_inserting_hook(self) -> bool:
        """
        Returns:
            bool: True if this instruction will require the yarn-inserting hook to be clear. False otherwise.
        """
        return self._required_clear_inserting_hook


class In_Instruction(Yarn_Carrier_Instruction):
    """
    Represents in-instructions that bring in a carrier without involving the yarn-inserting hook.
    """

    def __init__(self, carrier: int | Yarn_Carrier, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.In, carrier, comment)

    def will_update_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """
        Args:
            machine_state (Knitting_Machine): The current machine model to update.

        Returns:
            bool: True if the carrier being brought in is not active so that the instruction will have an effect. False otherwise.
        """
        return not machine_state.carrier_system[self.carrier].is_active

    def execute(self, machine_state: Knitting_Machine) -> bool:
        will_update = self.will_update_machine_state(machine_state)
        machine_state.bring_in(self.carrier_id)
        return will_update

    @staticmethod
    def execute_in(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> In_Instruction:
        """Execute an 'in' instruction to bring a carrier into the knitting area.

        Args:
            machine_state (Knitting_Machine): The current machine model to update.
            carrier (int | Yarn_Carrier): The carrier to execute with.
            comment (str, optional): Additional details to document in the knitout. Defaults to no comment.

        Returns:
            In_Instruction: The instruction that was executed.
        """
        instruction = In_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Inhook_Instruction(Hook_Instruction):

    def __init__(self, carrier_set: Yarn_Carrier | int, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Inhook, carrier_set, comment, requires_clear_inserting_hook=True)

    def will_update_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """
        Args:
            machine_state (Knitting_Machine): The current machine model to update.

        Returns:
            bool: True if the carrier being brought in is not active so that the instruction will have an effect. False otherwise.
        """
        return not machine_state.carrier_system[self.carrier].is_active

    def execute(self, machine_state: Knitting_Machine) -> bool:
        will_update = self.will_update_machine_state(machine_state)
        machine_state.in_hook(self.carrier_id)
        return will_update

    @staticmethod
    def execute_inhook(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Inhook_Instruction:
        """Execute an 'inhook' instruction to hook a carrier into position.

        Args:
            machine_state (Knitting_Machine): The current machine model to update.
            carrier (int | Yarn_Carrier): The carrier to execute with.
            comment (str, optional): Additional details to document in the knitout. Defaults to no comment.

        Returns:
            Inhook_Instruction: The instruction that was executed.
        """
        instruction = Inhook_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Releasehook_Instruction(Hook_Instruction):
    """An instruction that releases the starting tail of a carrier on the yarn-inserting hook."""

    def __init__(
        self,
        carrier: int | Yarn_Carrier,
        comment: None | str = None,
        preferred_release_direction: Carriage_Pass_Direction = Carriage_Pass_Direction.Leftward,
    ):
        """

        Args:
            carrier (int | Yarn_Carrier): The carrier to execute with.
            comment (str, optional): Additional details to document in the knitout. Defaults to no comment.
            preferred_release_direction (Carriage_Pass_Direction, optional): The preferred direction of operations proceeding this releasehook. Defaults to Leftward release.
        """
        super().__init__(Knitout_Instruction_Type.Releasehook, carrier, comment, requires_clear_inserting_hook=False)
        self._preferred_release_direction: Carriage_Pass_Direction = preferred_release_direction

    @property
    def preferred_release_direction(self) -> Carriage_Pass_Direction:
        """Get the preferred direction to release this carrier.

        Returns:
            The preferred direction to release this carrier in.
            Will default to leftward release.
        """
        return self._preferred_release_direction

    def will_update_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """
        Args:
            machine_state (Knitting_Machine): The machine state to test if this instruction will update it.

        Returns:
            bool: True the machine state has a hooked carrier to release. False otherwise.
        """
        return machine_state.carrier_system.hooked_carrier is not None

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if machine_state.carrier_system.hooked_carrier is None:
            warnings.warn(
                Mismatched_Releasehook_Warning(self.carrier_id),
                stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package(),
            )
            return False
        elif self.carrier_id != machine_state.carrier_system.hooked_carrier.carrier_id:
            warnings.warn(
                Mismatched_Releasehook_Warning(self.carrier_id),
                stacklevel=get_user_warning_stack_level_from_knitout_interpreter_package(),
            )
        machine_state.release_hook()
        return True

    @staticmethod
    def execute_releasehook(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Releasehook_Instruction:
        """Execute a 'releasehook' instruction to release a hooked carrier.

        Args:
            machine_state (Knitting_Machine): The current machine model to update.
            carrier (int | Yarn_Carrier): The carrier to execute with.
            comment (str, optional): Additional details to document in the knitout.

        Returns:
            Releasehook_Instruction: The instruction that was executed.
        """
        instruction = Releasehook_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Out_Instruction(Yarn_Carrier_Instruction):
    """An instruction that moves a carrier off of the machine bed without cutting the yarn."""

    def __init__(self, carrier: int | Yarn_Carrier, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Out, carrier, comment)

    def will_update_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """
        Args:
            machine_state (Knitting_Machine): The current machine model to update.

        Returns:
            bool: True if the carrier being outhooked is active and available to be removed. False, otherwise.
        """
        return machine_state.carrier_system[self.carrier].is_active

    def execute(self, machine_state: Knitting_Machine) -> bool:
        will_update = self.will_update_machine_state(machine_state)
        machine_state.out(self.carrier_id)
        return will_update

    @staticmethod
    def execute_out(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Out_Instruction:
        """Execute an 'out' instruction to move a carrier out of the knitting area.

        Args:
            machine_state (Knitting_Machine): The current machine model to update.
            carrier (int | Yarn_Carrier): The carrier to execute with.
            comment (str, optional): Additional details to document in the knitout.

        Returns:
            Out_Instruction: The instruction that was executed.
        """
        instruction = Out_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Outhook_Instruction(Hook_Instruction):
    """An instruction that uses the yarn-inserting hook to cut and remove an active carrier from the system."""

    def __init__(self, carrier_set: Yarn_Carrier | int, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Outhook, carrier_set, comment)

    def will_update_machine_state(self, machine_state: Knitting_Machine) -> bool:
        """
        Args:
            machine_state (Knitting_Machine): The current machine model to update.

        Returns:
            bool: True if the carrier being outhooked is active and available to be removed. False, otherwise.
        """
        return machine_state.carrier_system[self.carrier].is_active

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Execute the instruction on the machine state.

        Args:
            machine_state (Knitting_Machine): The machine state to update.

        Returns:
            bool: True if the process completes an update by cutting the carrier. False, otherwise.
        """
        will_update = self.will_update_machine_state(machine_state)
        machine_state.out_hook(self.carrier_id)
        return will_update

    @staticmethod
    def execute_outhook(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Outhook_Instruction:
        """Execute an 'outhook' instruction to hook a carrier out of position.

        Args:
            machine_state (Knitting_Machine): The current machine model to update.
            carrier (int | Yarn_Carrier): The carrier to execute with.
            comment (str, optional): Additional details to document in the knitout. Defaults to no comment.

        Returns:
            Outhook_Instruction: The instruction that was executed.
        """
        instruction = Outhook_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction
