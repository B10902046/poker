import json
from game.game import setup_config, start_poker
from agents.dqn_train import setup_ai as train_ai
from baseline0 import setup_ai as baseline0_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai
from baseline5 import setup_ai as baseline5_ai
from baseline6 import setup_ai as baseline6_ai
from baseline7 import setup_ai as baseline7_ai
players = [baseline7_ai(), baseline6_ai(), baseline5_ai(),baseline4_ai()]

## Play in interactive mode if uncomment
#config.register_player(name="me", algorithm=console_ai())
for _ in range(500):
    index = np.random.randint(0, len(players))
    player = players[index]
    config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
    config.register_player(name="ta", algorithm=player)
    config.register_player(name="me", algorithm=train_ai())
    game_result = start_poker(config, verbose=1)

print(json.dumps(game_result, indent=4))

