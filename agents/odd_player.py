from game.players import BasePokerPlayer
from src.compute_odd import *

def card_to_id(card):
    """
    Convert a card string (e.g., 'CA' for Ace of Clubs) to a unique ID from 0 to 51.
    """
    rank_map = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
    suit_map = {'C': 0, 'D': 1, 'H': 2, 'S': 3}
    
    rank = card[1]
    suit = card[0]
    
    rank_id = rank_map[rank]
    suit_id = suit_map[suit]
    
    card_id = suit_id + rank_id * 4
    return card_id

def convert_hole_cards_to_ids(hole_cards):
    """
    Convert a list of hole cards to their respective IDs.
    """
    return [card_to_id(card) for card in hole_cards]

class OddPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # already win
        if self.win:
            action, amount = valid_actions[0]["action"], valid_actions[0]["amount"]
            return action, amount
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
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
        
        secret_key = 0.75
        secret_key2 = 0.5

        if len(round_state["community_card"]) == 0:
            secret_key = 0.6
            secret_key2 = 0.4

        if win_rate >= secret_key:
            # allin
            if (valid_actions[2]["amount"]["min"] > 20):
                action, amount = valid_actions[2]["action"], valid_actions[2]["amount"]["max"]
            elif valid_actions[2]["amount"]["min"] > 0:
                action, amount = valid_actions[2]["action"], 20
            else:
                action, amount = valid_actions[1]["action"], valid_actions[1]["amount"]
        elif win_rate >= 0.6:
            # raise 2BB or call 10BB
            if valid_actions[2]["amount"]["min"] <= 20 and valid_actions[2]["amount"]["max"] > 0:
                action, amount = valid_actions[2]["action"], 20
            elif valid_actions[1]["amount"] <= 100:
                action, amount = valid_actions[1]["action"], valid_actions[1]["amount"]
            else:
                action, amount = valid_actions[0]["action"], valid_actions[0]["amount"]
        elif win_rate >= secret_key2:
            # check
            if valid_actions[1]["amount"] <= 50:
                action, amount = valid_actions[1]["action"], valid_actions[1]["amount"]
            else:
                action, amount = valid_actions[0]["action"], valid_actions[0]["amount"]
        # elif win_rate >= 0.2:
        #     if valid_actions[2]["amount"]["min"] <= 20 and valid_actions[2]["amount"]["max"] > 0:
        #         action, amount = valid_actions[2]["action"], 20
        #     elif valid_actions[1]["amount"] <= 30:
        #         action, amount = valid_actions[1]["action"], valid_actions[1]["amount"]
        #     else:
        #         action, amount = valid_actions[0]["action"], valid_actions[0]["amount"]
        else:
            # fold or check
            if valid_actions[1]["amount"] == 0:
                action, amount = valid_actions[1]["action"], valid_actions[1]["amount"]
            else:
                action, amount = valid_actions[0]["action"], valid_actions[0]["amount"]
        
        print(f"action: {action}")
        print(f"amount: {amount}")
        return action, amount  # action returned here is sent to the poker engine
        
    def receive_game_start_message(self, game_info):
        if game_info["seats"][0]["name"]=='me':
            self.index=0
        else:
            self.index=1
        self.win=False

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.win_line=1000 + 15 * ((20 - round_count) //2) + 10 * ((20 - round_count) % 2)

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        if round_state["seats"][self.index]["stack"] >= self.win_line:
            self.win = True


def setup_ai():
    return OddPlayer()
