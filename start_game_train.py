import json
from game.game import setup_config, start_poker
from agents.dqn_train import setup_ai as train_ai

from baseline7 import setup_ai as baseline7_ai

config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
config.register_player(name="ta", algorithm=baseline7_ai())
config.register_player(name="my ai", algorithm=train_ai())

## Play in interactive mode if uncomment
#config.register_player(name="me", algorithm=console_ai())
for _ in range(500):
    game_result = start_poker(config, verbose=1)

print(json.dumps(game_result, indent=4))
