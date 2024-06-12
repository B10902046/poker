from game.players import BasePokerPlayer
from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
from src.DQN_model import DQN
from src.utils import round_state_to_features
import random
import torch.nn as nn
import torch.optim as optim
import torch
from collections import deque

def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)

class TrainPlayer(BasePokerPlayer):
    def __init__(self, num_actions=8):
        self.DQN = DQN(num_actions=num_actions)
        self.target_DQN = DQN(num_actions=num_actions)
        self.DQN.apply(init_weights)
        self.target_DQN.load_state_dict(self.DQN.state_dict())
        for p in self.target_DQN.parameters():
            p.requires_grad = False

        self.replay_buffer = deque()  # Fixed-size 5000 replay buffer popleft()
        self.buffer_size = 5000
        self.optimizer = optim.Adam(self.DQN.parameters(), lr=1e-4)
        self.criterion = nn.MSELoss()
        self.num_actions = num_actions
        self.step = 0
        self.learning_freq = 1
        self.target_update_freq = 100
        self.learning_start_step = 1000
        self.checkpoint_period = 1000
        self.batch_size = 128
        self.gamma = 0.95
        self.epsilon = 1.0  # Initial exploration rate
        self.epsilon_decay = 0.995  # Epsilon decay rate
        self.min_epsilon = 0.2  # Minimum epsilon value

    def select_epsilon_greedy_action(self, state_feature):
        if random.random() > self.epsilon:
            output = self.DQN(torch.Tensor(state_feature))
            return int(torch.argmax(output).cpu())
        else:
            return random.randrange(self.num_actions)

    def declare_action(self, valid_actions, hole_card, round_state):
        state_feature = round_state_to_features(hole_card, round_state, self.game_info)
        state_feature.extend([s['stack'] for s in round_state['seats'] if s['uuid'] == self.uuid])
        state_feature.extend([s['stack'] for s in round_state['seats'] if s['uuid'] != self.uuid])
        if self.last_state is not None:
            # self.replay_buffer.append((self.last_state, self.last_action, reward, state_feature))
            self.cache.append((self.last_state, self.last_action, state_feature))
            print("add a record to the replay buffer: ", end="")
            # print((self.last_state, self.last_action, reward, state_feature))
        self.last_state = state_feature
        
        try:
            all_actions = [[valid_actions[0]["action"], valid_actions[0]["amount"]], [valid_actions[1]["action"], 50], [valid_actions[1]["action"], 100], [valid_actions[1]["action"], 150], [valid_actions[2]["action"], 20], [valid_actions[2]["action"], 40], [valid_actions[2]["action"], 80], [valid_actions[2]["action"], valid_actions[2]["amount"]["max"]]]
            
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
            
            if self.step < self.learning_start_step:
                action_id = random.choice(valid_action_id)
            else:
                if random.random() > self.epsilon:
                    output = self.DQN(torch.Tensor(state_feature))
                    # Create a subset of the tensor
                    subset = output[valid_action_id]
                    # Find the index of the maximum value within the subset
                    max_subset_index = torch.argmax(subset).item()
                    # Map back to the original index
                    action_id = valid_action_id[max_subset_index]
                else:
                    action_id = random.choice(valid_action_id)
            
            self.last_action = action_id
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)  # Decay epsilon

            if (action_id == 0):
                amount = 0
            elif (action_id <= 3):
                amount = valid_actions[1]["amount"]
            else:
                amount = all_actions[action_id][1]
            action = all_actions[action_id][0]

        except Exception as e:
            print(f"error in action selection: {e}")

        try:
            if self.step >= self.learning_start_step and self.step % self.learning_freq == 0:
                batch = random.sample(self.replay_buffer, self.batch_size)
                state_batch = torch.Tensor([record[0] for record in batch])
                action_batch = torch.Tensor([record[1] for record in batch]).to(dtype=torch.int64)
                reward_batch = torch.Tensor([record[2] for record in batch])
                nxt_state_batch = torch.Tensor([record[3] for record in batch])

                current_Q_values = self.DQN(state_batch).gather(1, action_batch.unsqueeze(1)).squeeze()
                next_Q_values = self.target_DQN(nxt_state_batch).detach().max(1)[0]
                target_Q_values = reward_batch + self.gamma * next_Q_values
                bellman_error = self.criterion(current_Q_values, target_Q_values)
                print(f"loss in step {self.step} is {bellman_error}")
                self.optimizer.zero_grad()
                bellman_error.backward()
                self.optimizer.step()
            if self.step % self.target_update_freq == 0 and self.step >= self.learning_start_step:
                self.target_DQN.load_state_dict(self.DQN.state_dict())
            if self.step % self.checkpoint_period == 0 and self.step >= self.learning_start_step:
                torch.save(self.DQN.state_dict(), f"src/model/model_{self.step}.pth")
        except Exception as e:
            print(f"error in training process at step {self.step}: {e}")

        self.step += 1
        return action, amount

    def receive_game_start_message(self, game_info):
        self.game_info = game_info
        #self.total_stack = game_info["player_num"] * game_info["rule"]["initial_stack"]
        self.last_state = None
        self.last_action = None
        # self.last_stack = game_info['rule']['initial_stack']

        self.round_stack = 0

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.round_stack = [s['stack'] for s in seats if s['uuid'] == self.uuid][0]
        self.cache = []

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        reward = [s['stack'] for s in round_state['seats'] if s['uuid'] == self.uuid][0] - self.round_stack
        for C in self.cache:
            self.replay_buffer.append((C[0], C[1], reward, C[2]))
            if self.step > self.buffer_size:
                self.replay_buffer.popleft()

        

def setup_ai():
    return TrainPlayer()
