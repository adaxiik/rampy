#!/usr/bin/env python3

# https://www.cs.vsb.cz/sawa/uti/slides/uti-06-cz.pdf
# 86

import typer

def main(program_path: str, print_parsed_program: bool = False):
    with open(program_path, 'r') as f:
        program_txt = f.read()

    from src.parse_program import ProgramParser as pp, FailedToParse

    try:
        parsed_program = pp.parse(program_txt)
    except FailedToParse as e:
        print(e)
        exit(1)

    if print_parsed_program:
        print(parsed_program)

    
    


if __name__ == '__main__':
    typer.run(main)

