import torch
from torch import nn
import numpy as np
import random
from func import *


# Seed 고정
def seed_everything(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if use multi-GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    random.seed(seed)


# loss function
def loss_fn(loss, pred, labels):
    if loss == "CEL":
        fn = nn.CrossEntropyLoss()
        return fn(pred, labels)
    elif loss == "FL":
        fn = FocalLoss(gamma=0.5).to(device)
        return fn(pred, labels)


# Accuracy 계산
def calc_accuracy(X, Y):
    max_vals, max_indices = torch.max(X, 1)
    train_acc = (max_indices == Y).sum().data.cpu().numpy() / max_indices.size()[0]
    return train_acc
