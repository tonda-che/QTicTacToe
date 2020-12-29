import tkinter as tk
import tkinter.messagebox as messagebox
from functools import partial
from pathlib import Path
import random
import json

class QTicTacToe(tk.Frame):
    LEARNING_RATE = 0.5
    DISCOUNT_FACTOR = 0.9

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
    winning_combinations = [["ul","um","ur"], ["cl","cm","cr"], ["ll", "lm", "lr"],
                            ["ul","cl","ll"], ["um", "cm", "lm"], ["ur","cr","lr"],
                            ["ul","cm","lr"], ["ur","cm","ll"]]

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_button_grid()
        self.initialize_model_weights()
        self.initialize_first_move()

    def initialize_first_move(self):
        if random.random() < 0.5:
            if messagebox.showinfo("OK","The machine starts"):
                self.play_turn(self.button_grid)
        else:
             messagebox.showinfo("OK","You start")


    def initialize_model_weights(self):
        path = Path('model_weights.json')
        if path.is_file():
            with open('model_weights.json', 'r') as json_file:
                model_weights = json.load(json_file)
        else:
            model_weights = dict({'0': dict(), '1': dict(), '2': dict(), '3': dict(), '4': dict(), '5': dict(), '6': dict(), '7': dict(), '8': dict(), '9': dict()})
        self.model_weights = model_weights

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

    def get_future_states(self, state, action):
        simplified_state = self.simplify(state)
        simplified_state[action] = "O"
        future_state_list = []
        for button, text in simplified_state.items():
            if text == "":
                state_copy = simplified_state.copy()
                state_copy[button] = "X"
                serialized_state_copy = self.serialize(state_copy)
                future_state_list.append(serialized_state_copy)
        return future_state_list

    def play_turn(self, state):
        simplified_state = self.simplify(state)
        serialized_state = self.serialize(simplified_state)
        number_turns_played = self.number_turns_played()
        self.last_number_turns = number_turns_played
        self.last_state = serialized_state

        # differentiate whether weights have been found
        if serialized_state in self.model_weights[number_turns_played].keys():
            actions = self.model_weights[number_turns_played][serialized_state]

        else:
            actions = dict()
            possible_action_list = self.get_possible_actions(simplified_state)

            # initialize weights for possible actions
            for action in possible_action_list:
                actions[action] = {"q_value": 1.0 / len(possible_action_list), "future_states": self.get_future_states(state, action)}
            self.model_weights[number_turns_played][serialized_state] = actions

        # make decision
        action_list = []
        prob_list = []
        for action, value in actions.items():
            action_list.append(action)
            prob_list.append(value["q_value"])
        choice = random.choices(action_list, weights=prob_list, k=1)[0]
        self.last_action = choice
        self.button_grid[choice]["text"] = "O"
        self.button_grid[choice]["state"] = "disabled"
        self.check_if_end(player="O")

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
        self.button_grid[command_name]["text"] = "X"
        self.button_grid[command_name]["state"] = "disabled"
        self.check_if_end(player="X")
        self.play_turn(self.button_grid)

    def check_if_end(self, player):
        state = self.simplify(self.button_grid)
        has_won = self.check_if_won(player, state)
        draw = self.check_if_draw()
        if has_won:
            if player == "X":
                if messagebox.showinfo("OK","You won"):
                    self.adjust_model_weights(self.last_state, self.last_number_turns, self.last_action, reward=0)
                    with open('model_weights.json', 'w') as json_file:
                        json.dump(self.model_weights, json_file)
                    root.destroy()
                    exit()
            elif player == "O":
                if messagebox.showinfo("OK","The machine won"):
                    self.adjust_model_weights(self.last_state, self.last_number_turns, self.last_action, reward=1)
                    with open('model_weights.json', 'w') as json_file:
                        json.dump(self.model_weights, json_file)
                    root.destroy()
                    exit()
            else:
                raise ValueError("Illegal Player")
        elif draw:
            if messagebox.showinfo("OK","Draw"):
                self.adjust_model_weights(self.last_state, self.last_number_turns, self.last_action, reward=0.5)
                with open('model_weights.json', 'w') as json_file:
                    json.dump(self.model_weights, json_file)
                root.destroy()
                exit()

    def adjust_model_weights(self, last_serialized_state, last_number_turns_played, last_action, reward):

        # adjust current q-value
        self.model_weights[last_number_turns_played][last_serialized_state][last_action]["q_value"] = reward

        # adjust previous q-value
        number_turns_played = int(last_number_turns_played) - 2
        while number_turns_played >= 0:
            # go through all states and actions
            for state in self.model_weights[str(number_turns_played)]:
                for action in self.model_weights[str(number_turns_played)][state].keys():
                    # get the current q value
                    current_q_value = self.model_weights[str(number_turns_played)][state][action]["q_value"]
                    future_state_q_value_list = []
                    # go through any potential futures states
                    for future_state in self.model_weights[str(number_turns_played)][state][action]["future_states"]:
                        # check if future state even exists
                        if future_state in self.model_weights[str(number_turns_played+2)].keys():

                            # take max of q-values of all future actions
                            future_action_q_value_list = []
                            for future_action in self.model_weights[str(number_turns_played+2)][future_state]:
                                future_action_q_value_list.append(self.model_weights[str(number_turns_played+2)][future_state][future_action]["q_value"])
                            future_state_q_value_list.append(max(future_action_q_value_list))

                    # check if any future states even in dictionary
                    if len(future_state_q_value_list) > 0:
                        new_q_value = min(future_state_q_value_list)
                        self.model_weights[str(number_turns_played)][state][action]["q_value"]  = current_q_value + self.LEARNING_RATE * self.DISCOUNT_FACTOR * (new_q_value - current_q_value)
            number_turns_played -= 2

    def check_if_draw(self):
        return self.number_turns_played() == '9'

    def number_turns_played(self):
        state = self.simplify(self.button_grid)
        return str(sum([0 if value == "" else 1 for value in state.values()]))

    def check_if_won(self, player, state):
        for combination in self.winning_combinations:
            criteria_fulfilled = True
            for entry in combination:
                criteria_fulfilled = criteria_fulfilled and state[entry] == player
            if criteria_fulfilled:
                return True
        return False

root = tk.Tk()
root.geometry("450x450")
root.resizable(False, False)
app = QTicTacToe(master=root)
app.mainloop()
