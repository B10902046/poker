CARDS = [
    0x18002, 0x14002, 0x12002, 0x11002, 0x28103, 0x24103, 0x22103, 0x21103, 0x48205, 0x44205,
    0x42205, 0x41205, 0x88307, 0x84307, 0x82307, 0x81307, 0x10840b, 0x10440b, 0x10240b, 0x10140b,
    0x20850d, 0x20450d, 0x20250d, 0x20150d, 0x408611, 0x404611, 0x402611, 0x401611, 0x808713,
    0x804713, 0x802713, 0x801713, 0x1008817, 0x1004817, 0x1002817, 0x1001817, 0x200891d, 0x200491d,
    0x200291d, 0x200191d, 0x4008a1f, 0x4004a1f, 0x4002a1f, 0x4001a1f, 0x8008b25, 0x8004b25,
    0x8002b25, 0x8001b25, 0x10008c29, 0x10004c29, 0x10002c29, 0x10001c29,
]

def compute_alive_cards(mask: int, number_of_cards: int, cards: List[Tuple[str, int]]) -> List[int]:
    result = []
    for i in range(number_of_cards):
        if (cards[i][1] & mask) == 0:
            result.append(i)
    return result

def heads_up_win_frequency(hand1, hand2, board):
    assert len(hand1) == 2
    assert len(hand2) <= 2
    assert len(board) in [0, 3, 4, 5]

    alive_cards = compute_alive_cards(hand1.get_mask() | hand2.get_mask() | board.get_mask() | dead_cards.get_mask(), number_of_cards, cards)
    assert len(alive_cards) >= 5 - len(board)
    
    hand1 = hand1 + board
    hand2 = hand2 + board
    
    match (len(board)):
        case (0):
            return heads_up_win_freq_0_0(hand1, heads_up_win_frequency, number_of_cards, cards) 
        case (3):
            return heads_up_win_freq_0(hand1, hand2, alive_cards, heads_up_win_freq_2_3)
        case (4):
            return heads_up_win_freq_0(hand1, hand2, alive_cards, heads_up_win_freq_2_4)
        case (5):
            return heads_up_win_freq_0(hand1, hand2, alive_cards, heads_up_win_freq_2_5)