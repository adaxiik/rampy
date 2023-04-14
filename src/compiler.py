from typing import Union
from .backend.c_backend import BackendC
from .backend.asm_backend import BackendAsm
from .instruction import *

Backend = Union[BackendC, BackendAsm]

class Compiler:
    def __init__(self, target: Backend):
        self.target = target

    def compile(self) -> str:
        program = self.target.program

        result = self.target.pre_compilation(program)
        result += self.target.header()

        for instruction in program:
            result += self.target.pre_instruction()
            if isinstance(instruction, SetValue):
                result += self.target.set_value(instruction.target_register, instruction.value)
            elif isinstance(instruction, SetRegister):
                result += self.target.set_register(instruction.target_register, instruction.source_register)
            elif isinstance(instruction, SetRegisterRegOpConst):
                result += self.target.set_register_reg_op_const(instruction.target_register, instruction.source_register, instruction.op, instruction.value)
            elif isinstance(instruction, SetRegisterRegOpReg):
                result += self.target.set_register_reg_op_reg(instruction.target_register, instruction.first_source_register, instruction.op, instruction.second_source_register)
            elif isinstance(instruction, Write):
                result += self.target.write(instruction.source_register)
            elif isinstance(instruction, Read):
                result += self.target.read(instruction.target_register)
            elif isinstance(instruction, Label):
                result += self.target.label(instruction.label)
            elif isinstance(instruction, UnconditionalJmpToLabel):
                result += self.target.unconditional_jmp_to_label(instruction.label)
            elif isinstance(instruction, UnconditionalJmpToInstruction):
                result += self.target.unconditional_jmp_to_instruction(instruction.instruction)
            elif isinstance(instruction, ConditionalJmpToInstruction):
                result += self.target.conditional_jmp_to_instruction(instruction.condition, instruction.instruction)
            elif isinstance(instruction, ConditionalJmpToLabel):
                result += self.target.conditional_jmp_to_label(instruction.condition, instruction.label)
            elif isinstance(instruction, Halt):
                result += self.target.halt()
            elif isinstance(instruction, Load):
                result += self.target.load(instruction.target_register, instruction.source_register)
            elif isinstance(instruction, Store):
                result += self.target.store(instruction.target_register, instruction.source_register)
            else:
                raise NotImplementedError(f"Unknown instruction: {repr(instruction)}")
            
            result += "\n"

        result += self.target.footer()
        return result