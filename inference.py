import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm
from itertools import chain
import torch

from eda_data import word_eda
from load_data import test_dataloader
from util import seed_everything
from model import model_tokenizer
from args import parser_args


if __name__ == "__main__":

    args = parser_args(mode="train")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed_everything(args.random_seed)
    test_data = pd.read_csv(f"{args.data_dir}test_data.csv")
    test_data["title"] = test_data["title"].apply(word_eda)
    tokenizer = model_tokenizer(args)
    test_loader = test_dataloader(test_data, tokenizer, args)
    # args.model_dir = f"{args.data_dir}{args.wandb_run_name}_{args.model_name}_{args.huggingface_model}"
    args.model_dir = f"{args.data_dir}{args.model_name}_final"

    for index, epoch in enumerate(list(map(int, args.best_epoch.split(',')))):
        model = torch.load(
            f"{args.model_dir}/{args.model_name}_fold{index+1}_epoch{epoch}.pt"
        )
        model.to(device)
        output_pred = []
        print(f"test start - fold {index+1} / best_epoch {epoch}")
        with torch.no_grad():
            model.eval()
            for ind, test_batch in tqdm(enumerate(test_loader)):
                input_ids = test_batch["input_ids"].to(device)
                attention_mask = test_batch["attention_mask"].to(device)
                if not args.model_name == "Xlm":
                    token_type_ids = test_batch["token_type_ids"].to(device)
                    output = model(input_ids, attention_mask, token_type_ids)
                else:
                    output = model(input_ids, attention_mask)
                logits = output[0]
                logits = logits.detach().cpu().numpy()
                # result = np.argmax(logits, -1)
                result = logits
                output_pred.append(result.tolist())
            labels = list(chain.from_iterable(output_pred))
            data = pd.read_csv(f"{args.data_dir}sample_submission.csv")
            data["topic_idx"] = labels
            data.to_csv(
                f"{args.model_dir}/{args.model_name}_fold{index+1}_epoch{epoch}.csv",
                index=False,
            )
