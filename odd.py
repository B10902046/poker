from enum import Enum
from typing import List, Tuple

# Constants (these should be defined according to your specific needs)
SUIT_SHIFT = 0  # Placeholder value
FLUSH_MASK = 0  # Placeholder value
OFFSET_SHIFT = 0  # Placeholder value
CARDS = [(0, 0)] * 52  # Placeholder value, should be filled with actual card data
LOOKUP = [0] * 8192  # Placeholder value, should be filled with actual lookup data
LOOKUP_FLUSH = [0] * 8192  # Placeholder value, should be filled with actual lookup data
OFFSETS = [0] * 8192  # Placeholder value, should be filled with actual offset data

class HandCategory(Enum):
    HighCard = 0
    OnePair = 1
    TwoPair = 2
    ThreeOfAKind = 3
    Straight = 4
    Flush = 5
    FullHouse = 6
    FourOfAKind = 7
    StraightFlush = 8

def get_hand_category(hand_rank: int) -> HandCategory:
    return HandCategory(hand_rank >> 12)

class Hand:
    def __init__(self, key: int = 0x3333 << SUIT_SHIFT, mask: int = 0):
        self.key = key
        self.mask = mask

    @classmethod
    def new(cls):
        return cls()

    @classmethod
    def from_slice(cls, cards: List[int]):
        hand = cls.new()
        for card in cards:
            hand = hand.add_card(card)
        return hand

    def is_empty(self) -> bool:
        return self.mask == 0

    def len(self) -> int:
        return bin(self.mask).count('1')

    def get_mask(self) -> int:
        return self.mask

    def contains(self, card: int) -> bool:
        return (self.mask & CARDS[card][1]) != 0

    def add_card(self, card: int) -> 'Hand':
        k, m = CARDS[card]
        return Hand(self.key + k, self.mask + m)

    def remove_card(self, card: int) -> 'Hand':
        k, m = CARDS[card]
        return Hand(self.key - k, self.mask - m)

    def evaluate(self) -> int:
        is_flush = self.key & FLUSH_MASK
        if is_flush > 0:
            flush_key = (self.mask >> (4 * (is_flush.bit_length() - 1))) & 0xFFFF
            return LOOKUP_FLUSH[flush_key]
        else:
            rank_key = self.key & 0xFFFFFFFF
            offset = OFFSETS[rank_key >> OFFSET_SHIFT]
            hash_key = rank_key + offset
            return LOOKUP[hash_key]

    def __add__(self, other: 'Hand') -> 'Hand':
        return Hand(self.key + other.key - (0x3333 << SUIT_SHIFT), self.mask + other.mask)

    def __iadd__(self, other: 'Hand') -> 'Hand':
        self.key += other.key
        self.key -= 0x3333 << SUIT_SHIFT
        self.mask += other.mask
        return self

    @staticmethod
    def from_str(hand_str: str) -> 'Hand':
        hand = Hand.new()
        chars = iter(hand_str)
        while True:
            try:
                rank_char = next(chars)
            except StopIteration:
                return hand
            suit_char = next(chars, None)
            if suit_char is None:
                raise ValueError("parse failed: expected suit character, but got EOF")
            rank_id = {
                '2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7,
                'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12
            }.get(rank_char.upper(), None)
            if rank_id is None:
                raise ValueError(f"parse failed: expected rank character, but got '{rank_char}'")
            suit_id = {
                'c': 0, 'd': 1, 'h': 2, 's': 3
            }.get(suit_char.lower(), None)
            if suit_id is None:
                raise ValueError(f"parse failed: expected suit character, but got '{suit_char}'")
            hand = hand.add_card(rank_id * 4 + suit_id)

from itertools import combinations
from collections import namedtuple

# Constants and data structures
NUMBER_OF_CARDS = 52
CARDS = [(rank, 1 << i) for i, rank in enumerate(range(NUMBER_OF_CARDS))]
HEADS_UP_WIN_FREQUENCY = [[0] * 13 for _ in range(13)]  # Placeholder for actual frequency data

Hand = namedtuple('Hand', ['cards', 'mask'])

def compute_alive_cards(mask):
    return [i for i in range(NUMBER_OF_CARDS) if (CARDS[i][1] & mask) == 0]

def heads_up_win_frequency(hand1, hand2, board, dead_cards):
    assert len(hand1.cards) == 2
    assert len(hand2.cards) <= 2
    assert len(board.cards) in {0, 3, 4, 5}
    assert len(hand1.cards) + len(hand2.cards) + len(board.cards) + len(dead_cards.cards) == len(set(hand1.cards + hand2.cards + board.cards + dead_cards.cards))
    
    alive_cards = compute_alive_cards(hand1.mask | hand2.mask | board.mask | dead_cards.mask)
    assert len(alive_cards) >= 5 - len(board.cards)
    
    hand1 = Hand(hand1.cards + board.cards, hand1.mask | board.mask)
    hand2 = Hand(hand2.cards + board.cards, hand2.mask | board.mask)
    
    match (len(hand2.cards) - len(board.cards), len(board.cards)):
        case (0, 0):
            return heads_up_win_freq_0_0(hand1) if len(dead_cards.cards) == 0 else heads_up_win_freq_0(hand1, hand2, alive_cards, heads_up_win_freq_2_0)
        case (0, 3):
            return heads_up_win_freq_0(hand1, hand2, alive_cards, heads_up_win_freq_2_3)
        case (0, 4):
            return heads_up_win_freq_0(hand1, hand2, alive_cards, heads_up_win_freq_2_4)
        case (0, 5):
            return heads_up_win_freq_0(hand1, hand2, alive_cards, heads_up_win_freq_2_5)
        case (1, 0):
            return heads_up_win_freq_1(hand1, hand2, alive_cards, heads_up_win_freq_2_0)
        case (1, 3):
            return heads_up_win_freq_1(hand1, hand2, alive_cards, heads_up_win_freq_2_3)
        case (1, 4):
            return heads_up_win_freq_1(hand1, hand2, alive_cards, heads_up_win_freq_2_4)
        case (1, 5):
            return heads_up_win_freq_1(hand1, hand2, alive_cards, heads_up_win_freq_2_5)
        case (2, 0):
            return heads_up_win_freq_2_0(hand1, hand2, alive_cards)
        case (2, 3):
            return heads_up_win_freq_2_3(hand1, hand2, alive_cards)
        case (2, 4):
            return heads_up_win_freq_2_4(hand1, hand2, alive_cards)
        case (2, 5):
            return heads_up_win_freq_2_5(hand1, hand2, alive_cards)
        case _:
            raise ValueError("Unreachable case")

def heads_up_win_freq_0_0(hand):
    cards = [i for i in range(NUMBER_OF_CARDS) if (CARDS[i][1] & hand.mask) != 0]
    rank1, suit1 = divmod(cards[0], 4)
    rank2, suit2 = divmod(cards[1], 4)
    return HEADS_UP_WIN_FREQUENCY[rank1 * 13 + rank2] if suit1 == suit2 else HEADS_UP_WIN_FREQUENCY[rank2 * 13 + rank1]

def heads_up_win_freq_0(hand1, hand2, alive_cards, func):
    result = [0, 0, 0]
    for i, j in combinations(range(len(alive_cards)), 2):
        new_hand2 = Hand(hand2.cards + [alive_cards[i], alive_cards[j]], hand2.mask | CARDS[alive_cards[i]][1] | CARDS[alive_cards[j]][1])
        remaining_alive_cards = [x for k, x in enumerate(alive_cards) if k not in {i, j}]
        tmp = func(hand1, new_hand2, remaining_alive_cards)
        result[0] += tmp[0]
        result[1] += tmp[1]
        result[2] += tmp[2]
    return tuple(result)

def heads_up_win_freq_1(hand1, hand2, alive_cards, func):
    result = [0, 0, 0]
    for i in range(len(alive_cards)):
        new_hand2 = Hand(hand2.cards + [alive_cards[i]], hand2.mask | CARDS[alive_cards[i]][1])
        remaining_alive_cards = [x for k, x in enumerate(alive_cards) if k != i]
        tmp = func(hand1, new_hand2, remaining_alive_cards)
        result[0] += tmp[0]
        result[1] += tmp[1]
        result[2] += tmp[2]
    return tuple(result)

def heads_up_win_freq_2_0(hand1, hand2, alive_cards):
    count = [0, 0, 0]
    for i, j, k, m, n in combinations(range(len(alive_cards)), 5):
        new_hand1 = Hand(hand1.cards + [alive_cards[i], alive_cards[j], alive_cards[k], alive_cards[m], alive_cards[n]], hand1.mask | CARDS[alive_cards[i]][1] | CARDS[alive_cards[j]][1] | CARDS[alive_cards[k]][1] | CARDS[alive_cards[m]][1] | CARDS[alive_cards[n]][1])
        new_hand2 = Hand(hand2.cards + [alive_cards[i], alive_cards[j], alive_cards[k], alive_cards[m], alive_cards[n]], hand2.mask | CARDS[alive_cards[i]][1] | CARDS[alive_cards[j]][1] | CARDS[alive_cards[k]][1] | CARDS[alive_cards[m]][1] | CARDS[alive_cards[n]][1])
        rank1 = new_hand1.evaluate()
        rank2 = new_hand2.evaluate()
        if rank1 > rank2:
            count[0] += 1
        elif rank1 < rank2:
            count[1] += 1
        else:
            count[2] += 1
    return tuple(count)

def heads_up_win_freq_2_3(hand1, hand2, alive_cards):
    count = [0, 0, 0]
    for i, j in combinations(range(len(alive_cards)), 2):
        new_hand1 = Hand(hand1.cards + [alive_cards[i], alive_cards[j]], hand1.mask | CARDS[alive_cards[i]][1] | CARDS[alive_cards[j]][1])
        new_hand2 = Hand(hand2.cards + [alive_cards[i], alive_cards[j]], hand2.mask | CARDS[alive_cards[i]][1] | CARDS[alive_cards[j]][1])
        rank1 = new_hand1.evaluate()
        rank2 = new_hand2.evaluate()
        if rank1 > rank2:
            count[0] += 1
        elif rank1 < rank2:
            count[1] += 1
        else:
            count[2] += 1
    return tuple(count)

def heads_up_win_freq_2_4(hand1, hand2, alive_cards):
    count = [0, 0, 0]
    for i in range(len(alive_cards)):
        new_hand1 = Hand(hand1.cards + [alive_cards[i]], hand1.mask | CARDS[alive_cards[i]][1])
        new_hand2 = Hand(hand2.cards + [alive_cards[i]], hand2.mask | CARDS[alive_cards[i]][1])
        rank1 = new_hand1.evaluate()
        rank2 = new_hand2.evaluate()
        if rank1 > rank2:
            count[0] += 1
        elif rank1 < rank2:
            count[1] += 1
        else:
            count[2] += 1
    return tuple(count)

def heads_up_win_freq_2_5(hand1, hand2, _):
    rank1 = hand1.evaluate()
    rank2 = hand2.evaluate()
    if rank1 > rank2:
        return (1, 0, 0)
    elif rank1 < rank2:
        return (0, 1, 0)
    else:
        return (0, 0, 1)







