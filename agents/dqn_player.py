from game.players import BasePokerPlayer
from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
from src.DQN_model import DQN
from src.utils import round_state_to_features
import random
import torch.nn as nn
import torch.optim as optim
import torch

class DQNPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"
    
    def __init__(self, num_actions = 7):
        self.DQN = DQN(num_actions=num_actions)
        self.DQN.load_state_dict(torch.load("src/model_7700.pth"))
        self.DQN.eval()
        self.num_actions = num_actions

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        state_feature = round_state_to_features(valid_actions, hole_card, round_state, self.game_info)
        # select the action
        try:
            raise_action_info = valid_actions[2]
            call_action_info = valid_actions[1]
            fold_action_info = valid_actions[0]

            # Log the valid actions for debugging
            print(f"Valid actions: {valid_actions}")

            all_actions = [[fold_action_info["action"],fold_action_info["amount"]],[call_action_info["action"],call_action_info["amount"]]]
            max_raise_amount = raise_action_info["amount"]["max"]
            min_raise_amount = raise_action_info["amount"]["min"]
            for i in range(self.num_actions-2):
                all_actions.append([raise_action_info["action"], min_raise_amount+(max_raise_amount-min_raise_amount)*i/4])
            
            # Log the constructed actions for debugging
            print(f"All actions: {all_actions}")

            output = self.DQN(state_feature)

            # Log the output tensor values for debugging
            print(f"Output tensor values: {output}")
            
            action_id = int(torch.argmax(output).cpu())
        except:
            print("error in action selection")
        action, amount = all_actions[action_id][0], all_actions[action_id][1]
        return action, amount  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.game_info = game_info
        self.total_stack = game_info["player_num"]*game_info["rule"]["initial_stack"]

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return DQNPlayer()