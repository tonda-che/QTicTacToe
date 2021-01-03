import random
import json
from pathlib import Path
import ui

class QTicTacToeEngine():
    LEARNING_RATE = 0.5
    DISCOUNT_FACTOR = 0.9

    winning_combinations = [["ul","um","ur"], ["cl","cm","cr"], ["ll", "lm", "lr"],
                            ["ul","cl","ll"], ["um", "cm", "lm"], ["ur","cr","lr"],
                            ["ul","cm","lr"], ["ur","cm","ll"]]

    def __init__(self):
        self.ui = ui.QTicTacToeUI(engine=self)
        self.initialize_model_weights()
        self.initialize_first_move()
        self.ui.master.mainloop()

    def self_play(self):
        simplified_state = dict({"ul": "","um": "","ur": "","cl": "","cm": "","cr": "","ll": "","lm": "","lr": ""})
        end = False
        player = "O"
        number_turns_played = 0
        print(f"Player {player} starts")
        while not end:
            previous_state = simplified_state
            simplified_state = self.invert_state(previous_state.copy())
            choice = self.make_decision(simplified_state = simplified_state)

            simplified_state[choice] = player

            has_won = self.check_if_won(player, simplified_state)
            draw = self.check_if_draw(simplified_state)
            end = has_won or draw

            number_turns_played += 1

            print()
            print(f"State {number_turns_played}:")
            print(self.get_serialized_state(simplified_state))
            print(f"by Player: {player}")
            print(f"Choice {choice}")
            print()

        last_serialized_state = self.get_serialized_state(self.invert_state(previous_state))
        print("Game End")
        print("Final State:")
        print(last_serialized_state)
        print("Choice:")
        print(choice)
        if has_won:
            reward = 1.0
        elif draw:
            reward = 0.5
        self.adjust_model_weights(last_serialized_state = last_serialized_state, last_number_turns_played = str(number_turns_played-1), last_action = choice, reward=reward)

    def invert_state(self, simplified_state):
        for action, text in simplified_state.items():
            if text == "X":
                simplified_state[action] = "O"
            if text == "O":
                simplified_state[action] = "X"
        return simplified_state

    def initialize_model_weights(self):
        path = Path('model_weights.json')
        if path.is_file():
            with open('model_weights.json', 'r') as json_file:
                model_weights = json.load(json_file)
        else:
            model_weights = dict({'0': dict(), '1': dict(), '2': dict(), '3': dict(), '4': dict(), '5': dict(), '6': dict(), '7': dict(), '8': dict(), '9': dict()})
        self.model_weights = model_weights

    def initialize_first_move(self):
        if random.random() < 0.5:
            self.ui.change_label("The machine starts")
            choice = self.make_decision(self.ui.get_simplified_state())
            self.ui.adjust_button_in_grid(choice, player = "O")
        else:
            self.ui.change_label("You start")

    def play_turn(self, choice, player):
        self.ui.adjust_button_in_grid(choice = choice, player = player)
        end, has_won, draw = self.check_if_end(player = player, simplified_state = self.ui.get_simplified_state())
        if end:
            self.ui.end_clean_up(player, has_won, draw)
            self.adjust_weights(player, has_won, draw)
        return end

    def get_serialized_state(self, simplified_state):
        serialized_state = ""
        count = 0
        for button_name in simplified_state.keys():
            if simplified_state[button_name] == "":
                serialized_state += "-"
            else:
                serialized_state += simplified_state[button_name]
            count += 1
            if count in [3,6]:
                serialized_state += "\n"
        return serialized_state

    def get_possible_actions(self, state):
        possible_actions = []
        for button_name in state.keys():
            if state[button_name] == "":
                possible_actions.append(button_name)
        return possible_actions

    def get_future_states(self, action, simplified_state):
        simplified_state = simplified_state.copy()
        simplified_state[action] = "O"
        future_state_list = []
        for button, text in simplified_state.items():
            if text == "":
                state_copy = simplified_state.copy()
                state_copy[button] = "X"
                serialized_state_copy = self.get_serialized_state(state_copy)
                future_state_list.append(serialized_state_copy)
        return future_state_list

    def make_decision(self, simplified_state):
        serialized_state = self.get_serialized_state(simplified_state)
        number_turns_played = self.number_turns_played(simplified_state)
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
                actions[action] = {"q_value": 1.0 / len(possible_action_list), "future_states": self.get_future_states(action, simplified_state)}
            self.model_weights[number_turns_played][serialized_state] = actions

        # make decision
        action_list = []
        prob_list = []
        for action, value in actions.items():
            action_list.append(action)
            prob_list.append(value["q_value"])

        # get choice based on probability weight
        choice = random.choices(action_list, weights=prob_list, k=1)[0]

        # save last state and action for the weight adjustment
        self.last_number_turns = number_turns_played
        self.last_state = serialized_state
        self.last_action = choice

        return choice

    def check_if_end(self, player, simplified_state):
        has_won = self.check_if_won(player, simplified_state)
        draw = self.check_if_draw(simplified_state)
        end = has_won or draw
        return end, has_won, draw

    def adjust_weights(self, player, has_won, draw):
        if has_won:
            if player == "X":
                self.save_weights(reward=0.0)
            elif player == "O":
                self.save_weights(reward=1.0)
            else:
                raise ValueError("Illegal Player")
        elif draw:
            self.save_weights(reward=0.5)

    def save_weights(self, reward):
        self.adjust_model_weights(self.last_state, self.last_number_turns, self.last_action, reward=0.5)
        with open('model_weights.json', 'w') as json_file:
            json.dump(self.model_weights, json_file)

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
                        # we can ignore the reward in each state as in the game there will only be a reward when winning (or losing)
                        self.model_weights[str(number_turns_played)][state][action]["q_value"]  = current_q_value + self.LEARNING_RATE * self.DISCOUNT_FACTOR * (new_q_value - current_q_value)
            number_turns_played -= 2

    def check_if_draw(self, simplified_state):
        return self.number_turns_played(simplified_state) == '9'

    def number_turns_played(self, simplified_state):
        non_empty_boxes = [0 if value == "" else 1 for value in simplified_state.values()]
        return str(sum(non_empty_boxes))

    def check_if_won(self, player, simplified_state):
        for combination in self.winning_combinations:
            criteria_fulfilled = True
            for entry in combination:
                criteria_fulfilled = criteria_fulfilled and simplified_state[entry] == player
            if criteria_fulfilled:
                return True
        return False

def main():
    QTicTacToeEngine()

if __name__ == '__main__':
    main()
