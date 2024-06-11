import torch.nn as nn
import torch.nn.functional as F
#in_features: 
#num_actions: fold call(0~3) call(3~6) call(6~9) call(9~12) call(12~allin) raise(3) raise(6) raise(9) raise(12) raise(15)
class DQN(nn.Module):
    def __init__(self, in_features=4, num_actions=7):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(in_features, 128)
        self.fc2 = nn.Linear(128, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, 64)
        self.fc5 = nn.Linear(64, num_actions)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        return self.fc5(x)