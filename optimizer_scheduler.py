import math
import numpy as np
from torch.optim.lr_scheduler import _LRScheduler, CosineAnnealingLR
from torch.optim import Adam, AdamW, optimizer
from transformers.optimization import get_cosine_with_hard_restarts_schedule_with_warmup
from func import *


def select_optimizer(model, args):

    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
        {
            "params": [
                p
                for n, p in model.named_parameters()
                if not any(nd in n for nd in no_decay)
            ],
            "weight_decay": 0.01,
        },
        {
            "params": [
                p
                for n, p in model.named_parameters()
                if any(nd in n for nd in no_decay)
            ],
            "weight_decay": 0.0,
        },
    ]
    if args.optimizer == "adamw":
        optimizer = AdamW(optimizer_grouped_parameters, lr=args.learning_rate)
    elif args.optimizer == "adam":
        optimizer = Adam(optimizer_grouped_parameters, lr=args.learning_rate)

    return optimizer


def select_scheduler(args, optimizer):
    t_total = args.train_loader_len * args.num_epochs
    warmup_step = int(t_total * args.warmup_ratio)
    if args.scheduler == "get_cosine":
        scheduler = get_cosine_with_hard_restarts_schedule_with_warmup(
            optimizer, num_warmup_steps=warmup_step, num_training_steps=t_total
        )
    elif args.scheduler == "custom":
        T_0 = int(np.ceil(t_total * 0.25))
        scheduler = CosineAnnealingWarmUpRestarts(
            optimizer,
            T_0 = T_0, 
            T_mult=2,
            eta_max=1e-4,
            T_up=int(args.warmup_ratio * T_0),
            gamma=0.8,
        )
    elif args.scheduler == "cosine":
        scheduler = CosineAnnealingLR(optimizer, T_max=10, eta_min=1e-7)
    return scheduler
