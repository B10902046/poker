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
    def __init__(self, num_actions=7):
        self.DQN = DQN(num_actions=num_actions)
        self.target_DQN = DQN(num_actions=num_actions)
        self.DQN.apply(init_weights)
        self.target_DQN.load_state_dict(self.DQN.state_dict())
        for p in self.target_DQN.parameters():
            p.requires_grad = False

        self.replay_buffer = deque(maxlen=10000)  # Fixed-size replay buffer
        self.optimizer = optim.Adam(self.DQN.parameters())
        self.criterion = nn.MSELoss()
        self.num_actions = num_actions
        self.step = 0
        self.learning_freq = 1
        self.target_update_freq = 8
        self.learning_start_step = 20
        self.checkpoint_period = 100
        self.batch_size = 16
        self.gamma = 0.99
        self.epsilon = 1.0  # Initial exploration rate
        self.epsilon_decay = 0.995  # Epsilon decay rate
        self.min_epsilon = 0.1  # Minimum epsilon value

    def select_epsilon_greedy_action(self, state_feature):
        if random.random() > self.epsilon:
            output = self.DQN(torch.Tensor(state_feature))
            return int(torch.argmax(output).cpu())
        else:
            return random.randrange(self.num_actions)

    def declare_action(self, valid_actions, hole_card, round_state):
        state_feature = round_state_to_features(valid_actions, hole_card, round_state, self.game_info)
        stack = valid_actions[2]["amount"]["max"]
        if stack < 0:
            stack = 0
        reward = (stack - self.last_stack) / self.total_stack
        if self.last_state is not None:
            self.replay_buffer.append((self.last_state, self.last_action, reward, state_feature))
            print("add a record to the replay buffer: ", end="")
            print((self.last_state, self.last_action, reward, state_feature))
        self.last_state = state_feature
        self.last_stack = stack
        
        try:
            raise_action_info = valid_actions[2]
            call_action_info = valid_actions[1]
            fold_action_info = valid_actions[0]
            all_actions = [[fold_action_info["action"], fold_action_info["amount"]], [call_action_info["action"], call_action_info["amount"]]]
            max_raise_amount = raise_action_info["amount"]["max"]
            min_raise_amount = raise_action_info["amount"]["min"]
            for i in range(self.num_actions - 2):
                all_actions.append([raise_action_info["action"], min_raise_amount + (max_raise_amount - min_raise_amount) * i / 4])
            
            if self.step < self.learning_start_step:
                action_id = random.randrange(self.num_actions)
            else:
                action_id = self.select_epsilon_greedy_action(state_feature)
            self.last_action = action_id
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
                torch.save(self.DQN.state_dict(), f"src/model_{self.step}.pth")
        except Exception as e:
            print(f"error in training process at step {self.step}: {e}")

        self.step += 1
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)  # Decay epsilon
        action, amount = all_actions[action_id][0], all_actions[action_id][1]
        return action, amount

    def receive_game_start_message(self, game_info):
        self.game_info = game_info
        self.total_stack = game_info["player_num"] * game_info["rule"]["initial_stack"]
        self.last_state = None
        self.last_action = None
        self.last_stack = game_info['rule']['initial_stack']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return TrainPlayer()
