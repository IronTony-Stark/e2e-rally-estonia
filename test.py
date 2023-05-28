import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import wandb
from torch import Tensor
from torch.nn import L1Loss, MSELoss, HuberLoss
from torch.utils.data import ConcatDataset, RandomSampler, WeightedRandomSampler
from torchsummary import summary
from dataloading.model import Camera, TurnSignal
from dataloading.nvidia import NvidiaTrainDataset, NvidiaValidationDataset, NvidiaWinterTrainDataset, \
    NvidiaWinterValidationDataset, AugmentationConfig
from dataloading.ouster import OusterTrainDataset, OusterValidationDataset
from efficient_net import effnetv2_s
from pilotnet import PilotNetConditional, PilotnetControl, PilotNet, CustomNetConditional
from trainer import ControlTrainer, ConditionalTrainer, PilotNetTrainer


if __name__ == "__main__":
    model = CustomNetConditional(3, 1, 3)
    summary(model, input_size=(3, 68, 264))
