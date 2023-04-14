from .instruction import *

class Interpreter:
    def __init__(self, program: Program):
        self.program: Program = program
        self.instruction_pointer: int = 1 # instruction are counted from 1
        self.registers: list[int] = [0] * 100
        self.labels: dict[str, int] = { instruction.label: index + 1 for index, instruction in enumerate(program) if isinstance(instruction, Label) }

    Halt = bool

    def _set_register(self, target_register: int, value: int):
        if len(self.registers) <= target_register:
            self.registers += [0] * (target_register - len(self.registers) + 1)

        self.registers[target_register] = value

    def _get_register(self, register: int) -> int:
        if len(self.registers) <= register:
            self.registers += [0] * (register - len(self.registers) + 1)

        return self.registers[register]
    
    def _apply_operation(self, operation: Op, a: int, b: int) -> int:
        if operation == Op.ADD:
            return a + b
        elif operation == Op.SUB:
            return a - b
        elif operation == Op.MUL:
            return a * b
        elif operation == Op.DIV:
            return a // b
        
        raise ValueError(f"Invalid operation: {operation}")
    
    def _apply_relation(self, relation: Rel, a: int, b: int) -> bool:
        if relation == Rel.LT:
            return a < b
        elif relation == Rel.GT:
            return a > b
        elif relation == Rel.LE:
            return a <= b
        elif relation == Rel.GE:
            return a >= b
        elif relation == Rel.EQ:
            return a == b
        elif relation == Rel.NE:
            return a != b
        
        raise ValueError(f"Invalid relation: {relation}")
    
    def _apply_condition(self, condition: ConditionWithConst or ConditionWithRegister) -> bool:
        if isinstance(condition, ConditionWithConst):
            return self._apply_relation(condition.rel, self._get_register(condition.register), condition.value)
        elif isinstance(condition, ConditionWithRegister):
            return self._apply_relation(condition.rel, self._get_register(condition.first_register), self._get_register(condition.second_register))
        else:
            raise ValueError(f"Invalid condition: {condition}")

    def run(self):
        while self.instruction_pointer < len(self.program):
            if self.step():
                break

    def reset(self):
        self.instruction_pointer = 1
        self.registers = [0] * 100
        

    def step(self, input_fn = input, output_fn = print) -> Halt:
        instruction = self.program[self.instruction_pointer - 1]
        if isinstance(instruction, Label):
            pass
        elif isinstance(instruction, SetValue):
            self._set_register(instruction.target_register, instruction.value)
        elif isinstance(instruction, SetRegister):
            self._set_register(instruction.target_register, self._get_register(instruction.source_register))
        elif isinstance(instruction, SetRegisterRegOpConst):
            result = self._apply_operation(instruction.op, self._get_register(instruction.source_register), instruction.value)
            self._set_register(instruction.target_register, result)
        elif isinstance(instruction, SetRegisterRegOpReg):
            result = self._apply_operation(instruction.op, self._get_register(instruction.first_source_register), self._get_register(instruction.second_source_register))
            self._set_register(instruction.target_register, result)
        elif isinstance(instruction, Load):
            source_reg = self._get_register(instruction.source_register)
            self._set_register(instruction.target_register, self._get_register(source_reg))
        elif isinstance(instruction, Store):
            target_reg = self._get_register(instruction.target_register)
            self._set_register(target_reg, self._get_register(instruction.source_register))
        elif isinstance(instruction, UnconditionalJmpToLabel):
            self.instruction_pointer = self.labels[instruction.label] - 1
        elif isinstance(instruction, UnconditionalJmpToInstruction):
            self.instruction_pointer = instruction.instruction - 1
        elif isinstance(instruction, ConditionalJmpToLabel):
            if self._apply_condition(instruction.condition):
                self.instruction_pointer = self.labels[instruction.label] - 1
        elif isinstance(instruction, ConditionalJmpToInstruction):
            if self._apply_condition(instruction.condition):
                self.instruction_pointer = instruction.instruction - 1
        elif isinstance(instruction, Read):
                self._set_register(instruction.target_register, int(input_fn()))
        elif isinstance(instruction, Write):
            output_fn(self._get_register(instruction.source_register))
        elif isinstance(instruction, Halt):
            return True
        else:
            raise ValueError(f"Invalid instruction: {instruction}")
        
        self.instruction_pointer += 1
        return False
        
    @property
    def current_instruction(self) -> Instruction:
        return self.program[self.instruction_pointer - 1]
