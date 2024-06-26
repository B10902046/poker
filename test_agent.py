import json
from game.game import setup_config, start_poker

import numpy as np
from tqdm import tqdm

from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai
from baseline5 import setup_ai as baseline5_ai
from baseline6 import setup_ai as baseline6_ai
from baseline7 import setup_ai as baseline7_ai

from src.agent import setup_ai as agent_ai


## Play in interactive mode if uncomment
#config.register_player(name="me", algorithm=console_ai())

players = [baseline7_ai(), baseline6_ai(), baseline5_ai(),baseline4_ai(), baseline3_ai(), baseline2_ai(), baseline1_ai()]
win = [0, 0, 0, 0, 0, 0, 0]
stake = [0, 0, 0, 0, 0, 0, 0]
for i, player in enumerate(players):
    for j in tqdm(range(10)):
        player = players[i]
        config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
        config.register_player(name="p1", algorithm=player)
        config.register_player(name="p2", algorithm=agent_ai())
        game_result = start_poker(config, verbose=1)
        if game_result["players"][0]["stack"] < game_result["players"][1]["stack"]:
            win[i] += 1
        stake[i] += game_result["players"][1]["stack"]
    print(f"odd v.s. {player}: {win[i] / 10}")
print(win)
print(stake)

