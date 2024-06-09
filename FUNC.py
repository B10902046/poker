from typing import List

def find_fast(u):
    u = (u + 0xe91aaa35) & 0xFFFFFFFF
    u ^= (u >> 16)
    u = (u + (u << 8)) & 0xFFFFFFFF
    u ^= (u >> 4)
    b = (u >> 8) & 0x1ff
    a = (u + (u << 2)) >> 19
    return a ^ HASH_ADJUST[b]

def eval_5cards_fast(c1, c2, c3, c4, c5):
    q = ((c1 | c2 | c3 | c4 | c5) >> 16)
    if (c1 & c2 & c3 & c4 & c5 & 0xf000) != 0:
        return FLUSHES[q]
    s = UNIQUE5[q]
    if s != 0:
        return s
    return HASH_VALUES[find_fast((c1 & 0xff) * (c2 & 0xff) * (c3 & 0xff) * (c4 & 0xff) * (c5 & 0xff))]

def eval_6cards_fast(c1, c2, c3, c4, c5, c6):
    hand = [c1, c2, c3, c4, c5, c6]
    best = 9999
    for perm in PERM6:
        subhand = [hand[i] for i in perm[:5]]
        q = eval_5cards_fast(*subhand)
        best = min(best, q)
    return best

def eval_7cards_fast(c1, c2, c3, c4, c5, c6, c7):
    hand = [c1, c2, c3, c4, c5, c6, c7]
    best = 9999
    for perm in PERM7:
        subhand = [hand[i] for i in perm[:5]]
        q = eval_5cards_fast(*subhand)
        best = min(best, q)
    return best

def eval_5cards(c1, c2, c3, c4, c5):
    return eval_5cards_fast(CARDS[c1], CARDS[c2], CARDS[c3], CARDS[c4], CARDS[c5])

def eval_6cards(c1, c2, c3, c4, c5, c6):
    return eval_6cards_fast(CARDS[c1], CARDS[c2], CARDS[c3], CARDS[c4], CARDS[c5], CARDS[c6])

def eval_7cards(c1, c2, c3, c4, c5, c6, c7):
    return eval_7cards_fast(CARDS[c1], CARDS[c2], CARDS[c3], CARDS[c4], CARDS[c5], CARDS[c6], CARDS[c7])

def compute_alive_cards(mask: int, NUMBER_OF_CARDS=52) -> List[int]:
    result = []
    for i in range(NUMBER_OF_CARDS):
        if (CARDS[i][1] & mask) == 0:
            result.append(i)
    return result

def enumerate_hand_category(hand, dead_cards, NUMBER_OF_CARDS=52) -> List[int]:
    assert 2 <= len(hand) <= 7
    assert (hand.get_mask() & dead_cards.get_mask()) == 0
    alive_cards = compute_alive_cards(hand.get_mask() | dead_cards.get_mask(), NUMBER_OF_CARDS)
    assert len(alive_cards) >= 7 - len(hand)
    
    if len(hand) == 2:
        return enumerate_hand_category_2(hand, alive_cards)
    elif len(hand) == 3:
        return enumerate_hand_category_3(hand, alive_cards)
    elif len(hand) == 4:
        return enumerate_hand_category_4(hand, alive_cards)
    elif len(hand) == 5:
        return enumerate_hand_category_5(hand, alive_cards)
    elif len(hand) == 6:
        return enumerate_hand_category_6(hand, alive_cards)
    elif len(hand) == 7:
        return enumerate_hand_category_7(hand, alive_cards)
    else:
        raise ValueError("Unreachable")

# Implement enumerate_hand_category_2 through enumerate_hand_category_7 similar to the Rust code
# Each function should iterate over combinations of alive cards, add them to the hand,
# evaluate the hand, and increment the corresponding category in the result array

# Example implementation for enumerate_hand_category_2
def enumerate_hand_category_2(hand, alive_cards) -> List[int]:
    result = [0] * NUM_HAND_CATEGORIES
    len_alive = len(alive_cards)
    for i in range(len_alive - 4):
        hand_with_card = hand.add_card(alive_cards[i])
        for j in range(i + 1, len_alive - 3):
            # Continue nesting loops and adding cards
            # Evaluate the hand and increment the corresponding category
            pass
    return result

