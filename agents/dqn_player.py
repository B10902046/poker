from game.players import BasePokerPlayer
from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
from src.DQN_model import DQN
from src.utils import round_state_to_features
import random
import torch.nn as nn
import torch.optim as optim
import torch
from src.compute_odd import *
from agents.odd_player import *

class DQNPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"
    
    def __init__(self, num_actions = 8):
        self.DQN = DQN(num_actions=num_actions)
        self.DQN.load_state_dict(torch.load("src/model/model2_20000.pth"))
        self.DQN.eval()
        self.num_actions = num_actions

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        if (self.win):
            return valid_actions[0]["action"], valid_actions[0]["amount"]
        
        state_feature = round_state_to_features(hole_card, round_state, self.game_info)
        state_feature.extend([s['stack'] for s in round_state['seats'] if s['uuid'] == self.uuid])
        state_feature.extend([s['stack'] for s in round_state['seats'] if s['uuid'] != self.uuid])
        
        try:
            all_actions = [[valid_actions[0]["action"], valid_actions[0]["amount"]], [valid_actions[1]["action"], 50], [valid_actions[1]["action"], 100], [valid_actions[1]["action"], 150], [valid_actions[2]["action"], 20], [valid_actions[2]["action"], 40], [valid_actions[2]["action"], 80], [valid_actions[2]["action"], valid_actions[2]["amount"]["max"]]]

            # Log the constructed actions for debugging
            #print(f"All actions: {all_actions}")

            valid_action_id = [0]
            if (valid_actions[1]["amount"]) <= 50:
                valid_action_id.append(1)
            elif (valid_actions[1]["amount"]) <= 100:
                valid_action_id.append(2)
            else:
                valid_action_id.append(3)
            if (valid_actions[2]["amount"]["min"] > 0):
                valid_action_id.append(7)
                if (valid_actions[2]["amount"]["min"] <= 80):
                    valid_action_id.append(6)
                if (valid_actions[2]["amount"]["min"] <= 40):
                    valid_action_id.append(5)
                if (valid_actions[2]["amount"]["min"] <= 20):
                    valid_action_id.append(4)

            output = self.DQN(torch.Tensor(state_feature))

            # Log the output tensor values for debugging
            print(f"Output tensor values: {output}")
            # Create a subset of the tensor
            subset = output[valid_action_id]
            # Find the index of the maximum value within the subset
            max_subset_index = torch.argmax(subset).item()
            # Map back to the original index
            action_id = valid_action_id[max_subset_index]

            #print(f"action_id: {action_id}")

            if (action_id == 0 and valid_actions[1]["amount"] > 0):
                amount = 0
            elif (action_id <= 3):
                amount = valid_actions[1]["amount"]
            else:
                amount = all_actions[action_id][1]
            action = all_actions[action_id][0]

            return action, amount  # action returned here is sent to the poker engine
        except:
            print("error in action selection")
        
    def receive_game_start_message(self, game_info):
        self.game_info = game_info
        self.total_stack = game_info["player_num"]*game_info["rule"]["initial_stack"]
        
        self.win=False

    def receive_round_start_message(self, round_count, hole_card, seats):
        remain_count = 20 + 1 - round_count
        self.win_line=1000 + 15 * ((remain_count) //2) + 10 * ((remain_count) % 2)
    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        a = [s['stack'] for s in round_state['seats'] if s['uuid'] == self.uuid]
        if a[0] >= self.win_line:
            self.win = True
        else:
            self.win=False

def setup_ai():
    return DQNPlayer()