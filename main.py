#!/usr/bin/env python3

# https://www.cs.vsb.cz/sawa/uti/slides/uti-06-cz.pdf
# 86

from typing import Tuple
import typer
from enum import Enum

class Action(Enum):
    COMPILE_TO_C = "compile-to-c"
    COMPILE_TO_ASM = "compile-to-asm"
    INTERPRET = "interpret"
    DEBUG = "debug"

SomeType = Tuple[int, str, Action]

def main(program_path: str
         , print_parsed_program: bool = False
         , action: Action = "interpret"
         , output_path: str = None):
    try:
        with open(program_path, 'r') as f:
            program_txt = f.read()
    except FileNotFoundError:
        print(f"File {program_path} not found")
        exit(1)
    

    from src.parse_program import ProgramParser as pp, FailedToParse

    try:
        parsed_program = pp.parse(program_txt)
    except FailedToParse as e:
        print(e)
        exit(1)

    if print_parsed_program:
        for instruction in parsed_program:
            print(repr(instruction))

    
    if action == Action.INTERPRET:
        from src.interpreter import Interpreter
        interpreter = Interpreter(parsed_program)
        interpreter.run()
        return
    
    if action == Action.DEBUG:
        from src.debugger import Debugger
        from src.interpreter import Interpreter
        try:
            interpreter = Interpreter(parsed_program)
            debugger = Debugger(interpreter)
            debugger.run()
        except Exception as e:
            # debugger controls terminal, so we need to print exception to file xd
            with open("debugger.log", 'w') as f:
                f.write(str(e))
        exit(0)
    
    if action == Action.COMPILE_TO_ASM:
        from src.compiler import Compiler
        from src.backend.backend_asm import BackendAsm
        compiler = Compiler(BackendAsm(parsed_program))
        if output_path:
            with open(output_path, 'w') as f:
                f.write(compiler.compile())
        else:
            print(compiler.compile())
        exit(0)

    if action == Action.COMPILE_TO_C:
        from src.compiler import Compiler
        from src.backend.backend_c import BackendC
        compiler = Compiler(BackendC(parsed_program))
        if output_path:
            with open(output_path, 'w') as f:
                f.write(compiler.compile())
        else:
            print(compiler.compile())
        exit(0)


if __name__ == '__main__':
    typer.run(main)

