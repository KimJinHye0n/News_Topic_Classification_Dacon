from transformers import (
    ElectraModel,
    ElectraTokenizer,
    ElectraConfig,
    ElectraForSequenceClassification,
)
from transformers import (
    BertModel,
    BertTokenizerFast,
    BertTokenizer,
    BertConfig,
    BertForSequenceClassification,
)
from transformers import (
    XLMRobertaModel,
    XLMRobertaConfig,
    XLMRobertaTokenizer,
    XLMRobertaForSequenceClassification,
)
from transformers import AutoTokenizer, AutoModel

from torch import nn
import torch


def model_tokenizer(args):
    if args.model_name == "Electra":
        return ElectraTokenizer.from_pretrained(args.huggingface_model)

    elif args.model_name == "Bert":
        if "kykim" in args.huggingface_model:
            return BertTokenizerFast.from_pretrained(args.huggingface_model)
        else:
            return BertTokenizer.from_pretrained(args.huggingface_model)

    elif args.model_name == "Xlm":
        if "klue" in args.huggingface_model:
            return BertTokenizer.from_pretrained(args.huggingface_model)
        else:
            return XLMRobertaTokenizer.from_pretrained(args.huggingface_model)


def model_select(args):
    if args.gru == 1:
        return model_plus_lstm(args.model_name, args.huggingface_model)

    if args.model_name == "Electra":
        model_config = ElectraConfig.from_pretrained(args.huggingface_model)
        model_config.num_labels = 7
        return ElectraForSequenceClassification.from_pretrained(
            args.huggingface_model, config=model_config
        )

    elif args.model_name == "Bert":
        model_config = BertConfig.from_pretrained(args.huggingface_model)
        model_config.num_labels = 7
        return BertForSequenceClassification.from_pretrained(
            args.huggingface_model, config=model_config
        )

    elif args.model_name == "Xlm":
        model_config = XLMRobertaConfig.from_pretrained(args.huggingface_model)
        model_config.num_labels = 7
        return XLMRobertaForSequenceClassification.from_pretrained(
            args.huggingface_model, config=model_config
        )


class model_plus_lstm(nn.Module):
    def __init__(self, model_name, huggingface_model):
        super().__init__()
        self.transformers_model = AutoModel.from_pretrained(
            huggingface_model, hidden_dropout_prob=0.0
        )
        if model_name == "Xlm":
            size = 1024
        else:
            size = 768
        self.gru = nn.GRU(
            input_size=size,
            hidden_size=size,
            num_layers=3,
            dropout=0.3,
            bidirectional=True,
            batch_first=True,
        )
        self.dense = nn.Linear(size * 2, 7, bias=True)

    def forward(self, input_ids, attention_mask, token_type_ids=None):
        if token_type_ids is not None:
            encoder = self.transformers_model(
                input_ids, attention_mask, token_type_ids
            )[0]
        else:
            encoder = self.transformers_model(input_ids, attention_mask)[0]
        output, h_n = self.gru(encoder)
        output_hidden = torch.cat((h_n[0], h_n[1]), dim=1)
        output = [self.dense(output_hidden)]
        return output
