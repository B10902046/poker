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
        self.DQN.load_state_dict(torch.load("src/model/model_9000.pth"))
        self.DQN.eval()
        self.num_actions = num_actions

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        state_feature = round_state_to_features(valid_actions, hole_card, round_state, self.game_info)
        
        hole_card_id = convert_hole_cards_to_ids(hole_card)
        hand1 = Hand.new()
        hand1 = hand1.add_card(hole_card_id[0])
        hand1 = hand1.add_card(hole_card_id[1])
        hand2 = Hand.new()
        board = Hand.new()
        for i in range(len(round_state["community_card"])):
            community_card = card_to_id(round_state["community_card"][i])
            board = board.add_card(community_card)
            hand1.cards += (community_card,)
            hand2.cards += (community_card,)
            hand1.mask += CARDS[community_card][1]
            hand2.mask += CARDS[community_card][1]
            hand1.key += CARDS[community_card][0]
            hand2.key += CARDS[community_card][0]
        a,b,c = heads_up_win_frequency(hand1, hand2, board)
        win_rate = a / (a+b+c)
        #----debug--------
        print(f"win_rate: {win_rate}")
        #---------------
        # select the action
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
            #print(f"Output tensor values: {output}")
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