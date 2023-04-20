from enum import Enum
from typing import List, Union

class Op(Enum):
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3

    @staticmethod
    def from_string(string: str) -> "Op":
        string = string.strip()
        if string == "+":
            return Op.ADD
        elif string == "-":
            return Op.SUB
        elif string == "*":
            return Op.MUL
        elif string == "/":
            return Op.DIV
        else:
            raise ValueError(f"Invalid op: {string}")
        
    def __str__(self) -> str:
        if self == Op.ADD:
            return "+"
        elif self == Op.SUB:
            return "-"
        elif self == Op.MUL:
            return "*"
        elif self == Op.DIV:
            return "/"
        else:
            raise ValueError(f"Invalid op: {self}")


class Rel(Enum):
    LT = 0
    GT = 1
    LE = 2
    GE = 3
    EQ = 4
    NE = 5

    @staticmethod
    def from_string(string: str) -> "Rel":
        string = string.strip()
        if string == "<":
            return Rel.LT
        elif string == ">":
            return Rel.GT
        elif string == "<=":
            return Rel.LE
        elif string == ">=":
            return Rel.GE
        elif string == "==":
            return Rel.EQ
        elif string == "!=":
            return Rel.NE
        else:
            raise ValueError(f"Invalid rel: {string}")
        
    def __str__(self) -> str:
        if self == Rel.LT:
            return "<"
        elif self == Rel.GT:
            return ">"
        elif self == Rel.LE:
            return "<="
        elif self == Rel.GE:
            return ">="
        elif self == Rel.EQ:
            return "=="
        elif self == Rel.NE:
            return "!="
        else:
            raise ValueError(f"Invalid rel: {self}")

Register = int
Value = int

class SetValue:
    def __init__(self, target_register: Register, value: Value):
        assert isinstance(target_register, int)
        assert isinstance(value, int)
        self.target_register = target_register
        self.value = value
    
    def __repr__(self):
        return f"SetValue(R{self.target_register}, {self.value})"
    
    def __str__(self):
        return f"R{self.target_register} := {self.value}"

class SetRegister:
    def __init__(self, target_register: Register, source_register: Register):
        assert isinstance(target_register, int)
        assert isinstance(source_register, int)
        self.target_register = target_register
        self.source_register = source_register
    
    def __repr__(self):
        return f"SetRegister(R{self.target_register}, R{self.source_register})"
    
    def __str__(self):
        return f"R{self.target_register} := R{self.source_register}"
    
class SetRegisterRegOpConst:
    def __init__(self, target_register: Register, source_register: Register, op: Op, value: Value):
        assert isinstance(target_register, int)
        assert isinstance(source_register, int)
        assert isinstance(op, Op)
        assert isinstance(value, int)
        self.target_register = target_register
        self.source_register = source_register
        self.op = op
        self.value = value
    
    def __repr__(self):
        return f"SetRegisterRegOpConst(R{self.target_register}, R{self.source_register}, {repr(self.op)}, {self.value})"
    
    def __str__(self):
        return f"R{self.target_register} := R{self.source_register} {self.op} {self.value}"

class SetRegisterRegOpReg:
    def __init__(self, target_register: Register, first_source_register: Register, op: Op, second_source_register: Register):
        assert isinstance(target_register, int)
        assert isinstance(first_source_register, int)
        assert isinstance(op, Op)
        assert isinstance(second_source_register, int)
        self.target_register = target_register
        self.first_source_register = first_source_register
        self.op = op
        self.second_source_register = second_source_register

    def __repr__(self):
        return f"SetRegisterRegOpReg(R{self.target_register}, R{self.first_source_register}, {repr(self.op)}, R{self.second_source_register})"

    def __str__(self):
        return f"R{self.target_register} := R{self.first_source_register} {self.op} R{self.second_source_register}"
class Load:
    def __init__(self, target_register: Register, source_register: Register):
        assert isinstance(target_register, int)
        assert isinstance(source_register, int)
        self.target_register = target_register
        self.source_register = source_register

    def __repr__(self):
        return f"Load(R{self.target_register}, R{self.source_register})"
    
    def __str__(self):
        return f"R{self.target_register} := [R{self.source_register}]"
    
class Store:
    def __init__(self, target_register: Register, source_register: Register):
        assert isinstance(target_register, int)
        assert isinstance(source_register, int)
        self.target_register = target_register
        self.source_register = source_register

    def __repr__(self):
        return f"Store(R{self.target_register}, R{self.source_register})"
    
    def __str__(self):
        return f"[R{self.target_register}] := R{self.source_register}"
    

class UnconditionalJmpToLabel:
    def __init__(self, label: str):
        assert isinstance(label, str)
        self.label = label

    def __repr__(self):
        return f"UnconditionalJumpToLabel({self.label})"
    
    def __str__(self):
        return f"goto {self.label}"
    
class UnconditionalJmpToInstruction:
    def __init__(self, instruction: int):
        assert isinstance(instruction, int)
        self.instruction = instruction

    def __repr__(self):
        return f"UnconditionalJumpToInstruction({self.instruction})"
    
    def __str__(self):
        return f"goto {self.instruction}"
    
class ConditionWithRegister:
    def __init__(self, first_register: Register, rel: Rel, second_register: Register):
        assert isinstance(first_register, int)
        assert isinstance(rel, Rel)
        assert isinstance(second_register, int)
        self.first_register = first_register
        self.rel = rel
        self.second_register = second_register

    def __repr__(self):
        return f"ConditionWithRegister(R{self.first_register}, {repr(self.rel)}, R{self.second_register})"
    
    def __str__(self):
        return f"R{self.first_register} {self.rel} R{self.second_register}"
    
class ConditionWithConst:
    def __init__(self, register: Register, rel: Rel, value: Value):
        assert isinstance(register, int)
        assert isinstance(rel, Rel)
        assert isinstance(value, int)
        self.register = register
        self.rel = rel
        self.value = value

    def __repr__(self):
        return f"ConditionWithConst(R{self.register}, {repr(self.rel)}, {self.value})"
    
    def __str__(self):
        return f"R{self.register} {self.rel} {self.value}"
    
class ConditionalJmpToLabel:
    def __init__(self, condition: Union[ConditionWithRegister, ConditionWithConst], label: str):
        assert isinstance(condition, ConditionWithRegister) or isinstance(condition, ConditionWithConst)
        assert isinstance(label, str)
        self.condition = condition
        self.label = label

    def __repr__(self):
        return f"ConditionalJumpToLabel({repr(self.condition)}, {self.label})"
    
    def __str__(self):
        return f"if ({self.condition}) goto {self.label}"
    
class ConditionalJmpToInstruction:
    def __init__(self, condition: Union[ConditionWithRegister, ConditionWithConst], instruction: int):
        assert isinstance(condition, ConditionWithRegister) or isinstance(condition, ConditionWithConst)
        assert isinstance(instruction, int)
        self.condition = condition
        self.instruction = instruction

    def __repr__(self):
        return f"ConditionalJumpToInstruction({repr(self.condition)}, {self.instruction})"
    
    def __str__(self):
        return f"if ({self.condition}) goto {self.instruction}"

class Read:
    def __init__(self, target_register: Register):
        assert isinstance(target_register, int)
        self.target_register = target_register

    def __repr__(self):
        return f"Read(R{self.target_register})"
    
    def __str__(self):
        return f"R{self.target_register} := read()"
    
class Write:
    def __init__(self, source_register: Register):
        assert isinstance(source_register, int)
        self.source_register = source_register

    def __repr__(self):
        return f"Write(R{self.source_register})"
    
    def __str__(self):
        return f"write(R{self.source_register})"
    
class Halt:
    def __repr__(self):
        return f"Halt()"
    
    def __str__(self):
        return f"halt"

class Label:
    def __init__(self, label: str):
        assert isinstance(label, str)
        self.label = label

    def __repr__(self):
        return f"Label({self.label})"
    
    def __str__(self):
        return f"{self.label}:"
    
Instruction = Union[SetValue
                    , SetRegister
                    , SetRegisterRegOpConst
                    , SetRegisterRegOpReg
                    , Load
                    , Store
                    , UnconditionalJmpToLabel
                    , UnconditionalJmpToInstruction
                    , ConditionalJmpToLabel
                    , ConditionalJmpToInstruction
                    , Read
                    , Write
                    , Halt
                    , Label]
Program = List[Instruction]
