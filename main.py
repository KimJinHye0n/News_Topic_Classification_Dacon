import argparse
import random
import numpy as np
import pandas as pd
import os
import wandb

from tqdm import tqdm

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

from sklearn.model_selection import StratifiedKFold

import warnings

from args import parser_args
from util import seed_everything, calc_accuracy, loss_fn
from eda_data import word_eda
from load_data import split_data
from model import model_tokenizer, model_select
from optimizer_scheduler import select_optimizer, select_scheduler

if __name__ == "__main__":

    warnings.filterwarnings(action="ignore")
    args = parser_args(mode="train")
    seed_everything(args.random_seed)
    
    if args.translate == 1 :
        train_data = pd.read_csv(f"{args.data_dir}train_data_pororo.csv")
    else :
        train_data = pd.read_csv(f"{args.data_dir}train_data.csv")
        train_data["title"] = train_data["title"].apply(word_eda)

    kfold = StratifiedKFold(
        n_splits=args.fold_num, shuffle=True, random_state=args.random_seed
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args.device = device

    tokenizer = model_tokenizer(args)

    wandb.login()

    for fold, (train_ids, dev_ids) in enumerate(
        kfold.split(train_data, train_data.topic_idx.values)
    ):
        train_loader, dev_loader = split_data(
            train_data, train_ids, dev_ids, tokenizer, args
        )
        model = model_select(args)
        args.train_loader_len = len(train_loader)
        optim = select_optimizer(model, args)
        scheduler = select_scheduler(args, optim)
        model.to(device)
        prev_acc = 0.0
        list_epoch = []
        wandb.init(
            project=args.wandb_project_name,
            name=f"{args.wandb_run_name}_{fold+1}",
            config=vars(args),
            job_type="train",
        )

        for epoch in range(args.num_epochs):
            model.train()
            print("train start")
            train_acc = 0.0
            test_acc = 0.0
            for i, train_batch in enumerate(train_loader):
                optim.zero_grad()
                input_ids = train_batch["input_ids"].to(device)
                attention_mask = train_batch["attention_mask"].to(device)
                labels = train_batch["idx"].long().to(device)
                if not args.model_name == "Xlm":
                    token_type_ids = train_batch["token_type_ids"].to(device)
                    output = model(
                        input_ids,
                        attention_mask=attention_mask,
                        token_type_ids=token_type_ids,
                    )
                else:
                    output = model(input_ids, attention_mask=attention_mask)
                loss = loss_fn(args.loss, output[0], labels)
                loss.backward()
                optim.step()
                scheduler.step()
                train_acc += calc_accuracy(output[0], labels)
                if i % args.log_interval == 0:
                    wandb.log({"train_loss": loss.data.cpu().numpy()})
                    print(
                        "epoch {} batch id {} loss {} train acc {}".format(
                            epoch + 1,
                            i + 1,
                            loss.data.cpu().numpy(),
                            train_acc / (i + 1),
                        )
                    )
            print("epoch {} train acc {}".format(epoch + 1, train_acc / (i + 1)))

            # validation
            with torch.no_grad():
                model.eval()
                print("test start")
                for j, dev_batch in enumerate(dev_loader):
                    input_ids = dev_batch["input_ids"].to(device)
                    attention_mask = dev_batch["attention_mask"].to(device)
                    labels = dev_batch["idx"].long().to(device)
                    if not args.model_name == "Xlm":
                        token_type_ids = dev_batch["token_type_ids"].to(device)
                        output = model(
                            input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                        )
                    else:
                        output = model(input_ids, attention_mask=attention_mask)
                    test_acc += calc_accuracy(output[0], labels)
                print("epoch {} test acc {}".format(epoch + 1, test_acc / (j + 1)))
                if prev_acc < test_acc / (j + 1):
                    print("most model test_acc {}".format(test_acc / (j + 1)))
                    if "/" in args.huggingface_model :
                        name = args.huggingface_model.replace("/", '_')
                    args.model_dir = f"{args.data_dir}{args.wandb_run_name}_{args.model_name}_{name}"
                    os.makedirs(args.model_dir, exist_ok=True)
                    torch.save(
                        model,
                        f"{args.model_dir}/{args.model_name}_fold{fold+1}_epoch{epoch+1}.pt",
                    )
                    prev_acc = test_acc / (j + 1)
                    list_epoch.append(epoch + 1)
            wandb.log(
                {
                    "epoch": epoch,
                    "train_acc": train_acc / (i + 1),
                    "valid_acc": test_acc / (j + 1),
                }
            )
        list_epoch.pop()
        for list_epoch_val in list_epoch:
            os.remove(
                f"{args.model_dir}/{args.model_name}_fold{fold+1}_epoch{list_epoch_val}.pt"
            )
        torch.cuda.empty_cache()
        wandb.join()
