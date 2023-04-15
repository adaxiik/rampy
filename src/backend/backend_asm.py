from typing import Dict
from ..instruction import *

class BackendAsm:
    DEFAULT_MEMORY_NAME = "memory"
    DEFAULT_MEMORY_CAPACITY_BYTES = 8 * 2048 
    def __init__(self, program: Program):
        self.program = program

        self.compiled_instructions: int = 0

        self.labels: Dict[str,str] = {}
        self.instruction_labels: Dict[int,str] = {}

    def map_label(self, label: str) -> str:
        if label not in self.labels:
            self.labels[label] = f"L_{len(self.labels)}"
        return self.labels[label]


    # godbolt <3
    def header(self) -> str:
        return """
BITS 64
    global _start
section .bss
""" + f"{self.DEFAULT_MEMORY_NAME} : resb {self.DEFAULT_MEMORY_CAPACITY_BYTES}" + """ 
section .text
write_:
    sub rsp, 40
    mov rcx, rdi
    xor r11d, r11d
    mov BYTE [rsp+21], 10
    test rdi, rdi
    jns .L2
    neg rcx
    mov r11d, 1
.L2:
    lea r8, [rsp+20]
    mov edi, 20
    mov r10, -3689348814741910323
.L3:
    mov rax, rcx
    movsx r9, edi
    sub r8, 1
    sub edi, 1
    mul r10
    mov rax, rcx
    shr rdx, 3
    lea rsi, [rdx+rdx*4]
    add rsi, rsi
    sub rax, rsi
    add eax, 48
    mov BYTE [r8+1], al
    mov rax, rcx
    mov rcx, rdx
    cmp rax, 9
    jg .L3
    test r11b, r11b
    je .L4
    movsx rdx, edi
    lea eax, [r9-2]
    movsx r9, edi
    mov BYTE [rsp+rdx], 45
    mov edi, eax
.L4:
    mov edx, 21
    lea rsi, [rsp+r9]
    xor eax, eax
    sub edx, edi
    mov edi, 1
    mov rax, 1
    syscall
    add rsp, 40
    ret

read_:
    sub rsp, 40
    mov edx, 22
    xor edi, edi
    xor eax, eax
    mov rsi, rsp
    mov rax, 0
    syscall
    movsx eax, BYTE  [rsp]
    cmp al, 45
    je .L30
    xor esi, esi
    xor ecx, ecx
    cmp al, 10
    je .L29
.L18:
    add rcx, rsp
    xor edx, edx
.L16:
    sub eax, 48
    lea rdx, [rdx+rdx*4]
    add rcx, 1
    cdqe
    lea rdx, [rax+rdx*2]
    movsx eax, BYTE  [rcx]
    cmp al, 10
    jne .L16
    mov rax, rdx
    neg rax
    test sil, sil
    cmovne rdx, rax
    add rsp, 40
    mov rax, rdx
    ret
.L30:
    movsx eax, BYTE [rsp+1]
    mov esi, 1
    mov ecx, 1
    cmp al, 10
    jne .L18
.L29:
    xor edx, edx
    add rsp, 40
    mov rax, rdx
    ret
_start:
"""
    
    def footer(self) -> str:
        return """
    mov rdi, 0
    mov rax, 60
    syscall"""
    
    def pre_compilation(self, program: Program) -> str:
        for instruction in program:
            if isinstance(instruction, UnconditionalJmpToInstruction) or isinstance(instruction, ConditionalJmpToInstruction):
                self.instruction_labels[instruction.instruction] = "IL_" + str(instruction.instruction)
        return ""
    
    def _indented(self, code: str) -> str:
        return "    " + code
    
    def pre_instruction(self) -> str:
        self.compiled_instructions += 1
        if self.compiled_instructions in self.instruction_labels:
            return f"{self.instruction_labels[self.compiled_instructions]}:\n"
        return ""

    def set_value(self, register: int, value: int) -> str:
        return self._indented(f"mov qword [memory + {register} * 8], {value}")
    
    def set_register(self, target_register: int, source_register: int) -> str:
        result = f"mov rdx, qword [memory + {source_register} * 8]\n"
        result += f"\tmov qword [memory + {target_register} * 8], rdx"
        return self._indented(result)

    def _compile_op(self, result_first_reg: str, second_reg: str, op: Op) -> str:
        if op == Op.ADD:
            return f"add {result_first_reg}, {second_reg}"
        elif op == Op.SUB:
            return f"sub {result_first_reg}, {second_reg}"
        elif op == Op.MUL:
            result = f"mov rax, {result_first_reg}\n"
            result += f"\tmov rdx, {second_reg}\n"
            result += f"\timul rdx\n"
            result += f"\tmov {result_first_reg}, rax"
            return result
        elif op == Op.DIV:
            result = f"mov rcx, {result_first_reg}\n"
            result += f"\tmov rbx, {second_reg}\n"
            result += f"\txor rdx, rdx\n"
            result += f"\tmov rax, rcx\n"
            result += f"\tcqo\n"
            result += f"\tidiv rbx\n"
            result += f"\tmov {result_first_reg}, rax"
            return result

    def set_register_reg_op_const(self, target_register: int, source_register: int, op: Op, value: int) -> str:
        result = f"mov rdx, qword [memory + {source_register} * 8]\n"
        result += f"\t{self._compile_op('rdx', value, op)}\n"
        result += f"\tmov qword [memory + {target_register} * 8], rdx"
        return self._indented(result)
    
    def set_register_reg_op_reg(self, target_register: int, first_source_register: int, op: Op, second_source_register: int) -> str:
        result = f"mov rdx, qword [memory + {first_source_register} * 8]\n"
        result += f"\tmov rax, qword [memory + {second_source_register} * 8]\n"
        result += f"\t{self._compile_op('rdx', 'rax', op)}\n"
        result += f"\tmov qword [memory + {target_register} * 8], rdx"
        return self._indented(result)
    
    def write(self, register: int) -> str:
        return self._indented(f"mov rdi, qword [memory + {register} * 8]\n\tcall write_")
    
    def read(self, register: int) -> str:
        return self._indented(f"call read_\n\tmov qword [memory + {register} * 8], rax")
    
    def label(self, label: str) -> str:
        return f"{self.map_label(label)}:"
    
    def unconditional_jmp_to_label(self, label: str) -> str:
        return self._indented(f"jmp {self.map_label(label)}")
    
    def _rel_to_jmp(self, rel: Rel) -> str:
        if rel == Rel.EQ:
            return "je"
        elif rel == Rel.NE:
            return "jne"
        elif rel == Rel.LT:
            return "jl"
        elif rel == Rel.LE:
            return "jle"
        elif rel == Rel.GT:
            return "jg"
        elif rel == Rel.GE:
            return "jge"
        else:
            raise ValueError(f"Unknown rel: {rel}")
    
    def _compile_condition(self, condition: ConditionWithRegister or ConditionWithConst) -> str:
        if isinstance(condition, ConditionWithRegister):
            result = f"mov rax, qword [memory + {condition.first_register} * 8]\n"
            result += f"\tmov rdx, qword [memory + {condition.second_register} * 8]\n"
            result += f"\tcmp rax, rdx"
            return result
        elif isinstance(condition, ConditionWithConst):
            return f"cmp qword [memory + {condition.register} * 8], {condition.value}"
        else:
            raise ValueError(f"Unknown condition: {condition}")

    def conditional_jmp_to_label(self, condition: ConditionWithRegister or ConditionWithConst, label: str) -> str:
        return self._indented(f"{self._compile_condition(condition)}\n\t{self._rel_to_jmp(condition.rel)} {self.map_label(label)}")

    def halt(self) -> str:
        return self._indented("mov rdi, 0\n\tmov rax, 60\n\tsyscall")

    def unconditional_jmp_to_instruction(self, instruction_to_jmp: int) -> str:
        return self._indented(f"jmp {self.instruction_labels[instruction_to_jmp]}")

    def conditional_jmp_to_instruction(self, condition: ConditionWithRegister or ConditionWithConst, instruction_to_jmp: int) -> str:
        return self._indented(f"{self._compile_condition(condition)}\n\t{self._rel_to_jmp(condition.rel)} {self.instruction_labels[instruction_to_jmp]}")

    def load(self, target_register: int, address_register: int) -> str:
        result = f"mov rdx, qword [memory + {address_register} * 8]\n"
        result += f"\tmov rax, qword [memory + rdx * 8]\n"
        result += f"\tmov qword [memory + {target_register} * 8], rax"
        return self._indented(result)
    
    def store(self, address_register: int, source_register: int) -> str:
        result = f"mov rdx, qword [memory + {address_register} * 8]\n"
        result += f"\tmov rax, qword [memory + {source_register} * 8]\n"
        result += f"\tmov qword [memory + rdx * 8], rax"
        return self._indented(result)