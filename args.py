import argparse
import os


def parser_args(mode="train"):

    parser = argparse.ArgumentParser()
    # wandb
    parser.add_argument("--wandb_project_name", required=True, type=str, help="name")
    parser.add_argument(
        "--wandb_run_name",
        required=True,
        type=str,
        help="initial_(model_name)_(addition_explain)",
    )
    # seed
    parser.add_argument("--random_seed", type=int, default=1333)
    # file
    parser.add_argument(
        "--data_dir",
        type=str,
        default="/content/drive/MyDrive/Colab Notebooks/data/news_headline_data/",
    )
    # data_augmentation
    parser.add_argument("--translate", type=int, default=0)
    parser.add_argument("--gpt_data", type=int, default=0)
    # train / test
    parser.add_argument("--max_len", type=int, default=64)
    parser.add_argument("--batch_size", type=int, default=32, help="xlm_large : 8")
    parser.add_argument("--num_worker", type=int, default=4)
    parser.add_argument("--warmup_ratio", type=float, default=0.01)
    parser.add_argument("--num_epochs", type=int, default=10)
    parser.add_argument("--log_interval", type=int, default=400, help="xlm_large : 400")
    parser.add_argument("--learning_rate", type=float, default=1e-5)
    parser.add_argument("--fold_num", type=int, default=5)
    parser.add_argument(
        "--model_name", type=str, default="Electra", help="Electra, Bert, Xlm"
    )
    parser.add_argument(
        "--huggingface_model",
        type=str,
        default="monologg/koelectra-base-v3-discriminator",
    )
    parser.add_argument("--loss", type=str, default="FL", help="CrossEntropy : CEL, Focal Loss : FL")
    parser.add_argument("--optimizer", type=str, default="adamw")
    parser.add_argument("--scheduler", type=str, default="get_cosine")
    parser.add_argument("--gru", type=int, default=0)
    parser.add_argument("--best_epoch", type=str, default="1,1,1,1,1")

    args = parser.parse_args()

    return args
