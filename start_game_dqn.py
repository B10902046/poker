import json
from game.game import setup_config, start_poker
from agents.dqn_player import setup_ai as dqn_ai

from baseline7 import setup_ai as baseline7_ai

config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
config.register_player(name="ta", algorithm=baseline7_ai())
config.register_player(name="my ai", algorithm=dqn_ai())

game_result = start_poker(config, verbose=1)

print(json.dumps(game_result, indent=4))
