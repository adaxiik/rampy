from .parser_combinators import ApplyParser

from .instruction import *
class FailedToParse(Exception):
    pass


class ProgramParser():
    @staticmethod
    def parse(input_str: str) -> Program:
        return [ProgramParser.parse_instruction(line) for line in input_str.splitlines() if line.strip() != ""]
    
    @staticmethod
    def parse_instruction(input_str: str) -> Instruction:
        pp = ProgramParser
        ins_parsers = [pp.parse_set_value
                       , pp.parse_set_register
                       , pp.parse_load
                       , pp.parse_store
                       , pp.parse_conditional_jmp
                       , pp.parse_unconditional_jmp
                       , pp.parse_read
                       , pp.parse_write
                       , pp.parse_halt
                       , pp.parse_label]
        
        for parser in ins_parsers:
            result = parser(input_str)
            if result is not None:
                return result
        
        raise FailedToParse(f"Failed to parse instruction from {input_str}")

    @staticmethod
    def parse_set_value(input_str: str) -> SetValue or None:
        if not(register_result := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = register_result.rest
        if not(assign_result := ApplyParser.assign_op(input_str)).is_valid:
            return None
        input_str = assign_result.rest
        if not(value_result := ApplyParser.sint(input_str)).is_valid:
            return None

        return SetValue(int(register_result.value[1:]), int(value_result.value))
    
    @staticmethod
    def parse_set_register(input_str: str) -> SetRegister or SetRegisterRegOpConst or SetRegisterRegOpReg or None:
        if not(target_register_result := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = target_register_result.rest
        
        if not(assign_result := ApplyParser.assign_op(input_str)).is_valid:
            return None
        input_str = assign_result.rest

        if not(first_source_register_result := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = first_source_register_result.rest

        if not(operator_result := ApplyParser.operator(input_str)).is_valid:
            return SetRegister(int(target_register_result.value[1:]), int(first_source_register_result.value[1:]))
        input_str = operator_result.rest

        second_source_register_result = ApplyParser.register(input_str)
        const_result = ApplyParser.uint(input_str)

        if second_source_register_result.is_valid:
            return SetRegisterRegOpReg(int(target_register_result.value[1:])
                                       , int(first_source_register_result.value[1:])
                                       , Op.from_string(operator_result.value.strip())
                                       , int(second_source_register_result.value[1:]))
        elif const_result.is_valid:
            return SetRegisterRegOpConst(int(target_register_result.value[1:])
                                         , int(first_source_register_result.value[1:])
                                         , Op.from_string(operator_result.value.strip())
                                         , int(const_result.value))
        return None

    @staticmethod
    def parse_load(input_str: str) -> Load or None:
        if not(target_register := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = target_register.rest

        if not(assign_op := ApplyParser.assign_op(input_str)).is_valid:
            return None
        input_str = assign_op.rest

        if not(lsparen := ApplyParser.lsparen(input_str)).is_valid:
            return None
        input_str = lsparen.rest

        if not(source_register := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = source_register.rest

        if not(rsparen := ApplyParser.rsparen(input_str)).is_valid:
            return None
        
        return Load(int(target_register.value[1:]), int(source_register.value[1:]))
    
    @staticmethod
    def parse_store(input_str: str) -> Store or None:
        if not(lsparen := ApplyParser.lsparen(input_str)).is_valid:
            return None
        input_str = lsparen.rest

        if not(target_register := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = target_register.rest

        if not(rsparen := ApplyParser.rsparen(input_str)).is_valid:
            return None
        input_str = rsparen.rest

        if not(assign_op := ApplyParser.assign_op(input_str)).is_valid:
            return None
        input_str = assign_op.rest

        if not(source_register := ApplyParser.register(input_str)).is_valid:
            return None
        
        return Store(int(target_register.value[1:]), int(source_register.value[1:]))
        
    @staticmethod
    def parse_conditional_jmp(input_str: str) -> ConditionalJmpToInstruction or ConditionalJmpToLabel or None:
        if not (if_result := ApplyParser.if_(input_str)).is_valid:
            return None
        input_str = if_result.rest

        if not (lparen := ApplyParser.lparen(input_str)).is_valid:
            return None
        input_str = lparen.rest

        if not (first_register := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = first_register.rest

        if not (rel_op := ApplyParser.rel_operator(input_str)).is_valid:
            return None
        input_str = rel_op.rest

        second_register = ApplyParser.register(input_str)
        const = ApplyParser.uint(input_str)

        condition : ConditionWithRegister or ConditionWithConst = None

        if second_register.is_valid:
            input_str = second_register.rest
            condition = ConditionWithRegister(int(first_register.value[1:]), Rel.from_string(rel_op.value.strip()), int(second_register.value[1:]))
        elif const.is_valid:
            input_str = const.rest
            condition = ConditionWithConst(int(first_register.value[1:]), Rel.from_string(rel_op.value.strip()), int(const.value))
        else:
            return None
        
        if not (rparen := ApplyParser.rparen(input_str)).is_valid:
            return None
        input_str = rparen.rest

        if not (goto_result := ApplyParser.goto_(input_str)).is_valid:
            return None
        input_str = goto_result.rest

        label = ApplyParser.label(input_str)
        instruction = ApplyParser.uint(input_str)

        if label.is_valid:
            return ConditionalJmpToLabel(condition, label.value)
        elif instruction.is_valid:
            return ConditionalJmpToInstruction(condition, int(instruction.value))

        return None
        
    @staticmethod
    def parse_unconditional_jmp(input_str: str) -> UnconditionalJmpToInstruction or UnconditionalJmpToLabel or None:
        if not (goto_result := ApplyParser.goto_(input_str)).is_valid:
            return None
        input_str = goto_result.rest
        
        label = ApplyParser.label(input_str)
        instruction = ApplyParser.uint(input_str)

        if label.is_valid:
            return UnconditionalJmpToLabel(label.value)
        elif instruction.is_valid:
            return UnconditionalJmpToInstruction(int(instruction.value))
        return None
    
    @staticmethod
    def parse_read(input_str: str) -> Read or None:
        # R1 := read()
        if not (target_register := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = target_register.rest

        if not (assign_op := ApplyParser.assign_op(input_str)).is_valid:
            return None
        input_str = assign_op.rest

        if not (read_result := ApplyParser.read(input_str)).is_valid:
            return None
        input_str = read_result.rest

        if not (lparen := ApplyParser.lparen(input_str)).is_valid:
            return None
        input_str = lparen.rest

        if not (rparen := ApplyParser.rparen(input_str)).is_valid:
            return None
        
        return Read(int(target_register.value[1:]))
    
    @staticmethod
    def parse_write(input_str: str) -> Write or None:
        if not (write_result := ApplyParser.write(input_str)).is_valid:
            return None
        input_str = write_result.rest

        if not (lparen := ApplyParser.lparen(input_str)).is_valid:
            return None
        input_str = lparen.rest

        if not (source_register := ApplyParser.register(input_str)).is_valid:
            return None
        input_str = source_register.rest

        if not (rparen := ApplyParser.rparen(input_str)).is_valid:
            return None
        
        return Write(int(source_register.value[1:]))
    
    @staticmethod
    def parse_halt(input_str: str) -> Halt or None:
        if not (halt_result := ApplyParser.halt(input_str)).is_valid:
            return None
        input_str = halt_result.rest

        return Halt()
    
    @staticmethod
    def parse_label(input_str: str) -> Label or None:
        if not (label_result := ApplyParser.label(input_str)).is_valid:
            return None
        input_str = label_result.rest


        if not (colon := ApplyParser.colon(input_str)).is_valid:
            return None
        
        return Label(label_result.value)