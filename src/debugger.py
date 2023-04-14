import string

from .instruction import Read
from .interpreter import Interpreter
import curses

class Tui:
    def __init__(self):
        self.screen: curses.window = None
        self.input_win: curses.window = None
        self.code_view_win: curses.window = None
        self.detail_win: curses.window = None

        self._init_tui()

    def __del__(self):
        self._destroy_tui()

    PREVIEW_WINDOW_HEIGHT = 6

    def _init_tui(self):
        self.screen = curses.initscr()
        curses.echo()
        curses.cbreak()
        curses.start_color()

        self.screen.keypad(True)
        self.screen.clear()
        self.screen.refresh()

        self.input_win = curses.newwin(3, curses.COLS, curses.LINES - 3, 0)
        self.input_win.box()
        self.code_win = curses.newwin(curses.LINES - self.PREVIEW_WINDOW_HEIGHT, curses.COLS // 2, 2, 0)
        self.code_win.box()
        self.detail_win = curses.newwin(curses.LINES - self.PREVIEW_WINDOW_HEIGHT, curses.COLS // 2, 2, curses.COLS // 2)
        self.detail_win.box()

        self.input_win.keypad(True)

    def _destroy_tui(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()


    def draw_input_window(self, message):
        self.input_win.clear()
        self.input_win.box()
        self.input_win.addstr(1, 1, message)
        self.input_win.noutrefresh()

    def draw_code_window(self, code):
        self.code_win.clear()
        self.code_win.box()
        for i, line in enumerate(code.splitlines()):
            if i >= self.get_code_window_height():
                break
            self.code_win.addstr(i + 1, 1, line)
        self.code_win.noutrefresh()

    def get_code_window_height(self):
        return curses.LINES - self.PREVIEW_WINDOW_HEIGHT - 2
    
    get_detail_window_height = get_code_window_height

    def draw_detail_window(self, detail):
        self.detail_win.clear()
        self.detail_win.box()
        for i, line in enumerate(detail.splitlines()):
            if i >= self.get_detail_window_height():
                break
            self.detail_win.addstr(i + 1, 1, line)
        self.detail_win.noutrefresh()


    def draw_info_bar(self, message):
        screen_width = self.screen.getmaxyx()[1]
        message = message + " " * (screen_width - len(message) - 1)
        self.screen.addstr(0, 0, message)
        self.screen.noutrefresh()

    def get_input(self):
        self.draw_input_window(">> ")
        command = self.input_win.getstr(1, 4, 50).decode().strip()
        return command
    
    def update(self):
        if curses.is_term_resized(curses.LINES, curses.COLS):
            curses.resizeterm(curses.LINES, curses.COLS)
            self.input_win.resize(3, curses.COLS)
            self.input_win.mvwin(curses.LINES - 3, 0)
            self.input_win.box()
            self.code_win.resize(curses.LINES - 6, curses.COLS // 2)
            self.code_win.box()
            self.detail_win.resize(curses.LINES - 6, curses.COLS // 2)
            self.detail_win.mvwin(2, curses.COLS // 2)
            self.detail_win.box()
        curses.doupdate()
        self.screen.refresh()

class Debugger:
    def __init__(self, interpretet: Interpreter):
        self.interpreter: Interpreter = interpretet
        self.breakpoints: list[int] = []

        self.tui = Tui()

        self.program_output: list[int] = []

    def _create_info(self) -> str:
        info = ""
        info += "Instruction pointer: {}\n".format(self.interpreter.instruction_pointer)
        info += "Breakpoints: {}\n".format(self.breakpoints)
        info += "Program output: {}\n".format(self.program_output)
        return info

    def _run_debugger(self, input_fn, output_fn):
        if self.interpreter.instruction_pointer in self.breakpoints:
            self.interpreter.step(input_fn=input_fn, output_fn=output_fn)

        while not self.interpreter.instruction_pointer in self.breakpoints \
              and self.interpreter.instruction_pointer < len(self.interpreter.program):
            
            self.interpreter.step(input_fn=input_fn, output_fn=output_fn)

    def _memory_view(self, start_register = 0) -> str:
        memory_view = ""
        if start_register < 0 or start_register >= len(self.interpreter.registers):
            return "Invalid register"
        
        for i in range(start_register, len(self.interpreter.registers)):
            memory_view += "R{}:\t {}\n".format(i, self.interpreter.registers[i])
        return memory_view
    
    def _help(self) -> str:
        help = ""
        help += "Commands:\n"
        help += "  run: Run the program until the next breakpoint\n"
        help += "  step: Step through the program\n"
        help += "  break <numbers>: Set a breakpoints at the given line\n"
        help += "  delete <numbers>: Delete the given breakpoints\n"
        help += "  memory <registers>: View the memory starting at the given register (default is 0)\n"
        help += "  reset: Reset the program\n"
        help += "  help: Show this help message\n"
        help += "  quit: Exit the debugger\n"
        return help
    
    # TODOOO int conversion checks
    def run(self):
        last_command = "run"
        detail_view_fn = self._create_info
        
        def input_fn():
            nonlocal detail_view_fn
            detail_view_fn = None
            self.tui.draw_detail_window("Waiting for input")
            self.tui.update()
            return int(self.tui.get_input())
                
        def output_fn(value):
            nonlocal current_details
            self.program_output.append(value)
            current_details = self._create_info()
        def get_code_view():
            # python go brr
            return "\n".join(["{}\t{}".format(i + self.interpreter.instruction_pointer , str(line)) if not i == 0 else "{} >\t{}".format(i + self.interpreter.instruction_pointer , str(line)) for i, line in enumerate(self.interpreter.program[self.interpreter.instruction_pointer - 1:])])

        current_code = get_code_view()

        # it is what it is
        while True:
            if detail_view_fn != None:
                current_details = detail_view_fn()

            self.tui.draw_code_window(current_code)
            self.tui.draw_detail_window(current_details)
            
            self.tui.draw_input_window(">> ")
            command = self.tui.get_input()
            if command == "":
                command = last_command

            if command.startswith("reset") or command.startswith("re"):
                self.interpreter.reset()
                self.program_output = []
                current_code = get_code_view()
                detail_view_fn = self._create_info
            elif command.startswith("quit") or command[0] == "q":
                break
            elif command.startswith("run") or command[0] == "r":
                self._run_debugger(input_fn, output_fn)
                current_code = get_code_view()
            elif command.startswith("break") or command[0] == "b":
                splitted = command.split(" ")
                if len(splitted) < 2:
                    detail_view_fn = None
                    current_details = "Missing breakpoint index"
                    continue
                detail_view_fn = self._create_info

                for i in range(1, len(splitted)):
                    if not splitted[i].isnumeric():
                        breakpoint = self.interpreter.labels[splitted[i]]
                    else:
                        breakpoint = int(splitted[i])
                    self.breakpoints.append(breakpoint)

            elif command.startswith("delete") or command[0] == "d":
                splitted = command.split(" ")
                if len(splitted) < 2:
                    detail_view_fn = None
                    current_details = "Missing breakpoint index"
                    continue

                detail_view_fn = self._create_info
                for i in range(1, len(splitted)):
                    breakpoint = int(splitted[i])
                    self.breakpoints.remove(breakpoint)

            elif command.startswith("step") or command[0] == "s":
                self.interpreter.step(input_fn=input_fn, output_fn=output_fn)
                current_code = get_code_view()
            elif command.startswith("info") or command[0] == "i":
                detail_view_fn = self._create_info
            elif command.startswith("memory") or command[0] == "m":
                splitted = command.split(" ")
                if len(splitted) < 2:
                    detail_view_fn = self._memory_view
                    continue
                detail_view_fn = None
                current_details = self._memory_view(int(splitted[1]))
            elif command.startswith("help") or command[0] == "h":
                detail_view_fn = None
                current_details = self._help()
            else:
                detail_view_fn = None
                current_details = "Unknown command \"{}\"".format(command)
                
            last_command = command

            self.tui.update()