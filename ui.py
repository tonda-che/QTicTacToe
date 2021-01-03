import tkinter as tk
from functools import partial

class QTicTacToeUI(tk.Frame):

    button_spec = {
        "ul": {"text": "Upper Left", "grid_row": 0, "grid_column": 0, "command": "ul"},
        "um": {"text": "Upper Middle", "grid_row": 0, "grid_column": 1, "command": "um"},
        "ur": {"text": "Upper Right", "grid_row": 0, "grid_column": 2, "command": "ur"},
        "cl": {"text": "Center Left", "grid_row": 1, "grid_column": 0, "command": "cl"},
        "cm": {"text": "Center Middle", "grid_row": 1, "grid_column": 1, "command": "cm"},
        "cr": {"text": "Center Right", "grid_row": 1, "grid_column": 2, "command": "cr"},
        "ll": {"text": "Lower Left", "grid_row": 2, "grid_column": 0, "command": "ll"},
        "lm": {"text": "Lower Middle", "grid_row": 2, "grid_column": 1, "command": "lm"},
        "lr": {"text": "Lower Right", "grid_row": 2, "grid_column": 2, "command": "lr"},
    }

    def __init__(self, engine=None):
        self.master = tk.Tk()
        self.master.wm_title("QTicTacToe")
        self.master.geometry("450x480")
        self.master.resizable(False, False)
        super().__init__(self.master)
        self.engine = engine
        self.pack()
        self.create_button_grid()
        self.create_controls()

    def create_button_grid(self):
        self.button_grid = dict()
        for button_name, button_dict in self.button_spec.items():
            button = tk.Button(self, width=16, height=9, text="")
            command = partial(self.button_press, button_dict["command"])
            button["command"] = command
            button.grid(row=button_dict["grid_row"], column=button_dict["grid_column"])
            self.button_grid[button_name] = button

    def create_controls(self):
        self.label = tk.Label(self, text="", width=16)
        self.label.grid(row=4, column=0)
        self.restart_button = tk.Button(self, text="Restart", width=16)
        self.restart_button .grid(row=4, column=1)
        self.restart_button["command"] = self.restart
        self.self_play_button = tk.Button(self, text="Self-Play", width=16)
        self.self_play_button.grid(row=4, column=2)
        self.self_play_button["command"] = self.engine.self_play

    def get_simplified_state(self):
        simplified_state = dict()
        for button_name in self.button_grid.keys():
            simplified_state[button_name] = self.button_grid[button_name]["text"]
        return simplified_state

    def button_press(self, command_name):
        end = self.engine.play_turn(choice=command_name, player="X")
        if not end:
            choice = self.engine.make_decision(self.get_simplified_state())
            self.engine.play_turn(choice=choice, player="O")

    def change_label(self, text):
        self.label["text"] = text

    def end_clean_up(self, player, has_won, draw):
        self.disable_grid()
        if has_won:
            if player == "X":
                self.change_label("You won")
            elif player == "O":
                self.change_label("The machine won")
            else:
                raise ValueError("Illegal Player")
        elif draw:
            self.change_label("Draw")

    def restart(self):
        self.change_label("")
        self.create_button_grid()
        self.engine.initialize_first_move()

    def adjust_button_in_grid(self, choice, player):
        self.button_grid[choice]["text"] = player
        self.button_grid[choice]["state"] = "disabled"

    def disable_grid(self):
        for command in self.button_grid.keys():
            self.button_grid[command]["state"] = "disabled"
