import torch.nn as nn
import torch.nn.functional as F
#in_features: 
#num_actions: fold call(0~5) call(5~10) call(10~allin) raise(2) raise(4) raise(8) allin
class DQN(nn.Module):
    def __init__(self, in_features=4, num_actions=8):
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