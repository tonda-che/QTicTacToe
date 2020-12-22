import tkinter as tk
from functools import partial
import random

class QTicTacToe(tk.Frame):
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

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_button_grid()
        self.model_weights = dict()

    def simplify(self, state):
        simplified_state = dict()
        for button_name in state.keys():
            simplified_state[button_name] = state[button_name]["text"]
        return simplified_state

    def serialize(self, state):
        serialized_state = ""
        for button_name in state.keys():
            if state[button_name] == "":
                serialized_state += "-"
            else:
                serialized_state += state[button_name]
        return serialized_state

    def get_possible_actions(self, state):
        possible_actions = []
        for button_name in state.keys():
            if state[button_name] == "":
                possible_actions.append(button_name)
        return possible_actions

    def play_turn(self, state):
        simplified_state = self.simplify(state)
        serialized_state = self.serialize(simplified_state)

        # differentiate whether weights have been found
        if serialized_state in self.model_weights.keys():
            actions = self.model_weights[serialized_state]
        else:
            actions = dict()
            possible_action_list = self.get_possible_actions(simplified_state)
            for action in possible_action_list:
                actions[action] = 1.0 / len(possible_action_list)
            self.model_weights[serialized_state] = actions

        # make decision
        action_list = []
        prob_list = []
        for action, prob in actions.items():
            action_list.append(action)
            prob_list.append(prob)
        choice = random.choices(action_list, weights=prob_list, k=1)[0]
        print(choice)
        self.button_grid[choice]["text"] = "O"
        self.button_grid[choice]["state"] = "disabled"

    def create_button_grid(self):
        self.button_grid = dict()
        for button_name, button_dict in self.button_spec.items():
            button = tk.Button(self)
            button["text"] = ""
            command = partial(self.button_press, button_dict["command"])
            button["command"] = command
            button["height"] = 9
            button["width"] = 16
            button.grid(row=button_dict["grid_row"], column=button_dict["grid_column"])
            self.button_grid[button_name] = button

    def button_press(self, command_name):
        print("{}".format(command_name))
        self.button_grid[command_name]["text"] = "X"
        self.button_grid[command_name]["state"] = "disabled"
        self.play_turn(self.button_grid)

root = tk.Tk()
root.geometry("450x450")
root.resizable(False, False)
app = QTicTacToe(master=root)
app.mainloop()
