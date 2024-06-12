from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
from src.compute_odd import *
import random

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

def round_state_to_features(hole_card, round_state, game_info):
    try:
        
        main_pot = round_state['pot']['main']['amount']
        
        street = -1
        if round_state['street'] == "preflop":
            street = 0
        elif round_state['street'] == "flop":
            street = 1
        elif round_state['street'] == "turn":
            street = 2
        else:
            street = 3
    except:
        print("error in block 1")
    
    try:
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

        features = [street, main_pot, win_rate]
        return features
    except:
        print("error in block 2")