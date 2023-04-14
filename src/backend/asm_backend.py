from ..instruction import *

class BackendAsm:
    def __init__(self, program: Program):
        self.program = program

    def header(self) -> str:
        return ""
    
    def footer(self) -> str:
        return ""
    
    def set_value(self, register: int, value: int) -> str:
        return f"R{register} = {value}"
    
    def set_register(self, target_register: int, source_register: int) -> str:
        return f"R{target_register} = R{source_register}"
    
    def set_register_reg_op_const(self, target_register: int, source_register: int, op: Op, value: int) -> str:
        return f"R{target_register} = R{source_register} {op} {value}"
    
    def set_register_reg_op_reg(self, target_register: int, first_source_register: int, op: Op, second_source_register: int) -> str:
        return f"R{target_register} = R{first_source_register} {op} R{second_source_register}"