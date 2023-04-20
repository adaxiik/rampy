from typing import Dict
from ..instruction import *

class BackendC:
    MEMORY_NAME = "memory"
    def __init__(self, program: Program):
        self.program = program
        self.compiled_instructions: int = 0

        self.labels: Dict[str,str] = {}
        self.instruction_labels: Dict[int,str] = {}

    def map_label(self, label: str) -> str:
        if label not in self.labels:
            self.labels[label] = f"L_{len(self.labels)}"
        return self.labels[label]

    def header(self) -> str:
        return """
#include <stdio.h>
#include <stdint.h>

int main(void) 
{
    int64_t """ + self.MEMORY_NAME + "[2048] = {0};\n"
    
    def footer(self) -> str:
        return "}"
    
    def _indented(self, code: str) -> str:
        return "    " + code
    
    def pre_compilation(self, program: Program) -> str:
        for instruction in program:
            if isinstance(instruction, UnconditionalJmpToInstruction) or isinstance(instruction, ConditionalJmpToInstruction):
                self.instruction_labels[instruction.instruction] = "IL_" + str(instruction.instruction)
        return ""
    
    def pre_instruction(self) -> str:
        self.compiled_instructions += 1
        if self.compiled_instructions in self.instruction_labels:
            return self._indented(f"{self.instruction_labels[self.compiled_instructions]}:\n")
        return ""

    def set_value(self, register: int, value: int) -> str:
        return self._indented(f"memory[{register}] = {value};")  
    
    def set_register(self, target_register: int, source_register: int) -> str:
        return self._indented(f"memory[{target_register}] = memory[{source_register}];")
    
    def set_register_reg_op_const(self, target_register: int, source_register: int, op: Op, value: int) -> str:
        return self._indented(f"memory[{target_register}] = memory[{source_register}] {op} {value};")
    
    def set_register_reg_op_reg(self, target_register: int, first_source_register: int, op: Op, second_source_register: int) -> str:
        return self._indented(f"memory[{target_register}] = memory[{first_source_register}] {op} memory[{second_source_register}];")
    
    def write(self, register: int) -> str:
        return self._indented(f"printf(\"%d\\n\", memory[{register}]);")
    
    def read(self, register: int) -> str:
        return self._indented(f"scanf(\"%d\", &memory[{register}]);")
    
    def label(self, label: str) -> str:
        return self._indented(f"{self.map_label(label)}:")
    
    def unconditional_jmp_to_label(self, label: str) -> str:
        return self._indented(f"goto {self.map_label(label)};")
    
    def conditional_jmp_to_label(self, condition:  Union[ConditionWithRegister, ConditionWithConst], label: str) -> str:
        if isinstance(condition, ConditionWithRegister):
            return self._indented(f"if (memory[{condition.first_register}] {condition.rel} memory[{condition.second_register}])\n\t\tgoto {self.map_label(label)};")
        elif isinstance(condition, ConditionWithConst):
            return self._indented(f"if (memory[{condition.register}] {condition.rel} {condition.value}) \n\t\tgoto {self.map_label(label)};")
        else:
            raise ValueError(f"Unknown condition: {condition}")

    def halt(self) -> str:
        return self._indented("return 0;")

    def unconditional_jmp_to_instruction(self, instruction_to_jmp: int) -> str:
        return self._indented(f"goto {self.instruction_labels[instruction_to_jmp]};")

    def conditional_jmp_to_instruction(self, condition:  Union[ConditionWithRegister, ConditionWithConst], instruction_to_jmp: int) -> str:
        if isinstance(condition, ConditionWithRegister):
            return self._indented(f"if (memory[{condition.first_register}] {condition.rel} memory[{condition.second_register}])\n\t\tgoto {self.instruction_labels[instruction_to_jmp]};")
        elif isinstance(condition, ConditionWithConst):
            return self._indented(f"if (memory[{condition.register}] {condition.rel} {condition.value}) \n\t\tgoto {self.instruction_labels[instruction_to_jmp]};")
        else:
            raise ValueError(f"Unknown condition: {condition}")   


    def load(self, target_register: int, address_register: int) -> str:
        return self._indented(f"memory[{target_register}] = memory[memory[{address_register}]];")
    
    def store(self, address_register: int, source_register: int) -> str:
        return self._indented(f"memory[memory[{address_register}]] = memory[{source_register}];")