
from string import ascii_letters
from typing import Callable


class ParseResult:
    def __init__(self, value, rest):
        self.value = value
        self.rest = rest

    def __repr__(self):
        return f"ParseResult({self.value}, {self.rest})"
    
    @staticmethod
    def invalid():
        return ParseResult(None, None)
    
    @property
    def is_valid(self):
        return self.value is not None and self.rest is not None
    
    @property
    def is_invalid(self):
        return not self.is_valid
    
    @property
    def has_value(self):
        return self.value is not None
    
    
Parser = Callable[[str], ParseResult]

class ParseCombinator:

    @staticmethod
    def create_char_parser(input_char: str) -> Parser:
        def parser(input_str) -> ParseResult:
            if input_str.startswith(input_char):
                return ParseResult(input_char, input_str[1:])
            else:
                return ParseResult.invalid()
        return parser

    @staticmethod
    def create_string_parser(input_str: str) -> Parser:
        return ParseCombinator.create_sequence_parser([ParseCombinator.create_char_parser(c) for c in input_str])

    @staticmethod
    def create_optional_parser(parser: Parser) -> Parser:
        def optional_parser(input_str) -> ParseResult:
            result = parser(input_str)
            if result.is_invalid:
                return ParseResult("", input_str)
            else:
                return result
        return optional_parser

    @staticmethod
    def create_alternative_parser(parsers: list[Parser]) -> Parser:
        def alternative_parser(input_str) -> ParseResult:
            for parser in parsers:
                result = parser(input_str)
                if result.is_valid:
                    return result
            return ParseResult.invalid()
        return alternative_parser

    @staticmethod
    def create_repeat_parser(parser: Parser, min_count: int = 0) -> Parser:
        def repeat_parser(input_str) -> ParseResult:
            values = []
            rest = input_str
            while True:
                result = parser(rest)
                if result.is_invalid:
                    break
                else:
                    values.append(result.value)
                    rest = result.rest
            if len(values) < min_count:
                return ParseResult.invalid()
            else:
                return ParseResult("".join(values), rest)
        return repeat_parser

    @staticmethod
    def create_sequence_parser(parsers: list[Parser]) -> Parser:
        def sequence_parser(string) -> ParseResult:
            values = []
            rest = string
            for parser in parsers:
                result = parser(rest)
                if result.is_invalid:
                    return ParseResult.invalid()
                else:
                    values.append(result.value)
                    rest = result.rest
            return ParseResult("".join(values), rest)
        return sequence_parser

class ApplyParser:
    digit = ParseCombinator.create_alternative_parser([ParseCombinator.create_char_parser(str(i)) for i in range(10)])
    whitespace = ParseCombinator.create_repeat_parser(ParseCombinator.create_alternative_parser([ParseCombinator.create_char_parser(' '), ParseCombinator.create_char_parser('\t')]))
    uint = ParseCombinator.create_repeat_parser(digit, min_count=1)
    register = ParseCombinator.create_sequence_parser([ParseCombinator.create_char_parser('R'), uint])
    assign_op = ParseCombinator.create_sequence_parser([whitespace, ParseCombinator.create_string_parser(":="), whitespace])
    lparen = ParseCombinator.create_sequence_parser([whitespace, ParseCombinator.create_char_parser('('), whitespace])
    rparen = ParseCombinator.create_sequence_parser([whitespace, ParseCombinator.create_char_parser(')'), whitespace])
    lsparen = ParseCombinator.create_sequence_parser([whitespace, ParseCombinator.create_char_parser('['), whitespace])
    rsparen = ParseCombinator.create_sequence_parser([whitespace, ParseCombinator.create_char_parser(']'), whitespace])
    operator = ParseCombinator.create_sequence_parser([whitespace
                                                       , ParseCombinator.create_alternative_parser([ParseCombinator.create_char_parser('+')
                                                                                                    , ParseCombinator.create_char_parser('-')
                                                                                                    , ParseCombinator.create_char_parser('*')
                                                                                                    , ParseCombinator.create_char_parser('/')])
                                                    , whitespace])
    rel_operator = ParseCombinator.create_sequence_parser([whitespace
                                                              , ParseCombinator.create_alternative_parser([ParseCombinator.create_string_parser("==")
                                                                                                              , ParseCombinator.create_string_parser("!=")
                                                                                                                , ParseCombinator.create_string_parser("<=")
                                                                                                                , ParseCombinator.create_string_parser(">=")
                                                                                                                , ParseCombinator.create_char_parser('<')
                                                                                                                , ParseCombinator.create_char_parser('>')])
                                                              , whitespace])

    
    label = ParseCombinator.create_sequence_parser([ParseCombinator.create_repeat_parser(ParseCombinator.create_alternative_parser([ParseCombinator.create_char_parser(c) for c in ascii_letters]), min_count=1)
                                                    , ParseCombinator.create_repeat_parser(ParseCombinator.create_alternative_parser([*[ParseCombinator.create_char_parser(c) for c in ascii_letters]
                                                                                                                                      , uint
                                                                                                                                      , ParseCombinator.create_char_parser('_')]), min_count=0)])
    sint = ParseCombinator.create_sequence_parser([ParseCombinator.create_optional_parser(ParseCombinator.create_char_parser('-'))
                                                   , uint])
    
    ignore_case_if = ParseCombinator.create_alternative_parser([ParseCombinator.create_string_parser("IF"), ParseCombinator.create_string_parser("if")])
    ignore_case_goto = ParseCombinator.create_alternative_parser([ParseCombinator.create_string_parser("GOTO"), ParseCombinator.create_string_parser("goto")])
    ignore_case_read = ParseCombinator.create_alternative_parser([ParseCombinator.create_string_parser("READ"), ParseCombinator.create_string_parser("read")])
    ignore_case_write = ParseCombinator.create_alternative_parser([ParseCombinator.create_string_parser("WRITE"), ParseCombinator.create_string_parser("write")])
    ignore_case_halt = ParseCombinator.create_alternative_parser([ParseCombinator.create_string_parser("HALT"), ParseCombinator.create_string_parser("halt")])

    if_ = ParseCombinator.create_sequence_parser([whitespace, ignore_case_if, whitespace])
    goto_ = ParseCombinator.create_sequence_parser([whitespace, ignore_case_goto, whitespace])
    read = ParseCombinator.create_sequence_parser([whitespace, ignore_case_read, whitespace])
    write = ParseCombinator.create_sequence_parser([whitespace, ignore_case_write, whitespace])
    halt = ParseCombinator.create_sequence_parser([whitespace, ignore_case_halt, whitespace])