import torch
import torch.nn as nn
from vit_pytorch import ViT
from torchvision.models.swin_transformer import SwinTransformer, Swin_B_Weights, Swin_S_Weights, Swin_T_Weights
from torchvision.models import swin_b, swin_s, swin_t


class PilotNet(nn.Module):
    """
    Network from 'End to End Learning for Self-Driving Cars' paper:
    https://arxiv.org/abs/1604.07316
    """

    def __init__(self, n_input_channels=3, n_outputs=1):
        super(PilotNet, self).__init__()

        self.features = nn.Sequential(
            nn.BatchNorm2d(n_input_channels),
            nn.Conv2d(n_input_channels, 24, 5, stride=2),
            nn.BatchNorm2d(24),
            nn.LeakyReLU(),
            nn.Conv2d(24, 36, 5, stride=2),
            nn.BatchNorm2d(36),
            nn.LeakyReLU(),
            nn.Conv2d(36, 48, 5, stride=2),
            nn.BatchNorm2d(48),
            nn.LeakyReLU(),
            nn.Conv2d(48, 64, 3, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(),
            nn.Conv2d(64, 64, 3, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(),
            nn.Flatten()
        )

        self.regressor = nn.Sequential(
            nn.Linear(1664, 100),
            nn.BatchNorm1d(100),
            nn.LeakyReLU(),
            nn.Linear(100, 50),
            nn.BatchNorm1d(50),
            nn.LeakyReLU(),
            nn.Linear(50, 10),
            nn.LeakyReLU(),
            nn.Linear(10, n_outputs),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.regressor(x)
        return x


class PilotNetConditional(nn.Module):
    """
    Network from 'End-to-end Driving via Conditional Imitation Learning' paper:
    https://arxiv.org/abs/1710.02410

    There is separate policy branch for each road selection, by default 3 for going straight, turning left and right.
    """

    def __init__(self, n_input_channels=3, n_outputs=1, n_branches=1):
        super(PilotNetConditional, self).__init__()

        self.features = nn.Sequential(
            nn.BatchNorm2d(n_input_channels),
            nn.Conv2d(n_input_channels, 24, 5, stride=2),
            nn.BatchNorm2d(24),
            nn.LeakyReLU(),
            nn.Conv2d(24, 36, 5, stride=2),
            nn.BatchNorm2d(36),
            nn.LeakyReLU(),
            nn.Conv2d(36, 48, 5, stride=2),
            nn.BatchNorm2d(48),
            nn.LeakyReLU(),
            nn.Conv2d(48, 64, 3, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(),
            nn.Conv2d(64, 64, 3, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(),
            nn.Flatten()
        )

        self.conditional_branches = nn.ModuleList([
            nn.Sequential(
                nn.Linear(1664, 100),
                nn.BatchNorm1d(100),
                nn.LeakyReLU(),
                nn.Linear(100, 50),
                nn.BatchNorm1d(50),
                nn.LeakyReLU(),
                nn.Linear(50, 10),
                nn.LeakyReLU(),
                nn.Linear(10, n_outputs),
            ) for i in range(n_branches)
        ])

    def forward(self, x):
        x = self.features(x)
        x = torch.cat([out(x) for out in self.conditional_branches], dim=1)
        return x


# ViT is too fat, consider using Swin instead
class ViTNetConditional(nn.Module):
    def __init__(self, n_input_channels=3, n_outputs=1, n_branches=3):
        super(ViTNetConditional, self).__init__()

        self.features = ViT(
            image_size=(68, 264),
            patch_size=4,
            num_classes=128,
            dim=256,
            depth=3,
            heads=4,
            mlp_dim=512,
            dropout=0.1,
            emb_dropout=0.1
        )

        self.conditional_branches = nn.ModuleList([
            nn.Sequential(
                nn.Linear(128, 100),
                nn.BatchNorm1d(100),
                nn.LeakyReLU(),
                nn.Linear(100, 50),
                nn.BatchNorm1d(50),
                nn.LeakyReLU(),
                nn.Linear(50, 10),
                nn.LeakyReLU(),
                nn.Linear(10, n_outputs),
            ) for _ in range(n_branches)
        ])

    def forward(self, x):
        x = self.features(x)
        x = torch.cat([out(x) for out in self.conditional_branches], dim=1)
        return x


class SwinNetConditional(nn.Module):
    def __init__(self, n_input_channels=3, n_outputs=1, n_branches=3, type='small'):
        super(SwinNetConditional, self).__init__()

        if type == 'base':
            self.features = swin_b(weights=Swin_B_Weights.DEFAULT)
        elif type == 'small':
            self.features = swin_s(weights=Swin_S_Weights.DEFAULT)
        else:
            self.features = swin_t(weights=Swin_T_Weights.DEFAULT)

        self.conditional_branches = nn.ModuleList([
            nn.Sequential(
                nn.Linear(1000, 100),
                nn.BatchNorm1d(100),
                nn.LeakyReLU(),
                nn.Linear(100, 50),
                nn.BatchNorm1d(50),
                nn.LeakyReLU(),
                nn.Linear(50, 10),
                nn.LeakyReLU(),
                nn.Linear(10, n_outputs),
            ) for _ in range(n_branches)
        ])

    def forward(self, x):
        x = self.features(x)
        x = torch.cat([out(x) for out in self.conditional_branches], dim=1)
        return x


class PilotnetControl(nn.Module):
    """
    Network from 'Urban Driving with Conditional Imitation Learning' paper:
    https://arxiv.org/abs/1912.00177

    Conditonal control is concatenated with input features to each policy branchy
    """

    def __init__(self, n_input_channels=3, n_outputs=1):
        super(PilotnetControl, self).__init__()

        self.features = nn.Sequential(
            nn.BatchNorm2d(n_input_channels),
            nn.Conv2d(n_input_channels, 24, 5, stride=2),
            nn.BatchNorm2d(24),
            nn.LeakyReLU(),
            nn.Conv2d(24, 36, 5, stride=2),
            nn.BatchNorm2d(36),
            nn.LeakyReLU(),
            nn.Conv2d(36, 48, 5, stride=2),
            nn.BatchNorm2d(48),
            nn.LeakyReLU(),
            nn.Conv2d(48, 64, 3, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(),
            nn.Conv2d(64, 64, 3, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(),
            nn.Flatten()
        )

        self.regressor1 = nn.Sequential(
            nn.Linear(1667, 100),
            nn.BatchNorm1d(100),
            nn.LeakyReLU(),
        )

        self.regressor2 = nn.Sequential(
            nn.Linear(103, 50),
            nn.BatchNorm1d(50),
            nn.LeakyReLU(),
        )

        self.regressor3 = nn.Sequential(
            nn.Linear(53, 10),
            nn.LeakyReLU(),
            nn.Linear(10, n_outputs),
        )

    def forward(self, x, control):
        x = self.features(x)
        x = self.regressor1(torch.cat([x, control], dim=1))
        x = self.regressor2(torch.cat([x, control], dim=1))
        x = self.regressor3(torch.cat([x, control], dim=1))
        return x
