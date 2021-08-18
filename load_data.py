import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from eda_data import word_eda


def tokenized_dataset(dataset, tokenizer, max_len):
    tokenized_sentences = tokenizer(
        list(dataset["title"]),
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_len,
    )
    return tokenized_sentences


class Headline_Dataset(Dataset):
    def __init__(self, tokenized_dataset, idx):
        self.tokenized_dataset = tokenized_dataset
        self.idx = idx

    def __getitem__(self, ind):
        item = {
            key: torch.tensor(val[ind]) for key, val in self.tokenized_dataset.items()
        }
        item["idx"] = torch.tensor(self.idx[ind])
        return item

    def __len__(self):
        return len(self.idx)


def pororo_data(df):
    df_origin = df.loc[:, ["index", "title", "topic_idx"]]
    
    # 한 - 영 - 한 데이터 추가
    df_en_ko = df.loc[:, ["index", "title_en_ko", "topic_idx"]]
    df_en_ko.rename(columns={"title_en_ko": "title"}, inplace=True)

    # 한 - 일 - 한 데이터 추가
    # df_ja_ko = df.loc[:, ["index", "title_ja_ko", "topic_idx"]]
    # df_ja_ko.rename(columns={"title_ja_ko": "title"}, inplace=True)

    df_concat = pd.concat([df_origin, df_en_ko], axis=0)
    return df_concat

def gpt_plus(df) :
    gpt = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/data/news_headline_data/gpt_it.csv")
    gpt['topic_idx'] = 0
    gpt.rename(columns={'Unnamed: 0' : 'index'}, inplace=True)
    gpt.title = gpt.title.apply(word_eda)
    df_concat = pd.concat([df, gpt], axis=0)
    return df_concat

def split_data(train_data, train_idx, dev_idx, tokenizer, config):
    train_dataset = train_data.loc[train_idx]
    dev_dataset = train_data.loc[dev_idx]
    if config.translate == 1:
        train_dataset = pororo_data(train_dataset)
    if config.gpt_data == 1 :
        train_dataset = gpt_plus(train_dataset) # gpt 파일 추가 삭제해도됨
    train_label = train_dataset.topic_idx.values
    dev_label = dev_dataset.topic_idx.values
    tokenized_trainset = tokenized_dataset(train_dataset, tokenizer, config.max_len)
    tokenized_devset = tokenized_dataset(dev_dataset, tokenizer, config.max_len)
    trainset = Headline_Dataset(tokenized_trainset, train_label)
    devset = Headline_Dataset(tokenized_devset, dev_label)
    train_loader = DataLoader(
        trainset,
        batch_size=config.batch_size,
        num_workers=config.num_worker,
        shuffle=True,
    )
    dev_loader = DataLoader(
        devset,
        batch_size=config.batch_size,
        num_workers=config.num_worker,
        shuffle=False,
    )
    return train_loader, dev_loader


def test_dataloader(test_data, tokenizer, config):
    test_data["idx"] = 0
    test_dataset = test_data
    test_dataset = tokenized_dataset(test_dataset, tokenizer, config.max_len)
    test_dataset = Headline_Dataset(test_dataset, test_data.idx.values)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)
    return test_loader
