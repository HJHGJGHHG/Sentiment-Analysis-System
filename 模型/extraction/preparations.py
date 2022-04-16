import json
import paddle
import random
import numpy as np
from tqdm import tqdm
from collections import defaultdict
from paddle.io import Dataset, DataLoader
from paddlenlp.data import Pad, Stack, Tuple

id2label = {0: 'O', 1: 'B-Aspect', 2: 'I-Aspect', 3: 'B-Opinion', 4: 'I-Opinion'}
label2id = {'O': 0, 'B-Aspect': 1, 'I-Aspect': 2, 'B-Opinion': 3, 'I-Opinion': 4}


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    paddle.seed(seed)


def load_data(data_path):
    with open(data_path, "r", encoding="utf-8") as f:
        data = {"text": [], "label": []}
        for line in f.readlines():
            text, label = line.split("\t")
            text = text[:-1] if text[-1] == "\n" else text
            label = label[:-1] if label[-1] == "\n" else label
            label = label.split(" ")
            text = list(text)
            assert len(text) == len(label), f"{text},  {label}"
            data["text"].append(text)
            data["label"].append(label)

        return data


class Extracion_Dataset(Dataset):
    def __init__(self, args, data, is_test=False):
        super(Extracion_Dataset, self).__init__()
        self.args = args
        self.data = data  # dict: {"text":[["string"]], "label":[[""string]]}
        self.tokenizer = args.tokenizer
        self.is_test = is_test

    def __len__(self):
        return len(self.data["text"])

    def __getitem__(self, idx):
        return self._convert_to_tensors(idx)

    def _convert_to_tensors(self, idx):
        encoded_inputs = self.args.tokenizer(
            self.data["text"][idx],
            is_split_into_words=True,
            max_seq_len=self.args.max_seq_len,
            return_length=True)
        if not self.is_test:
            label = [label2id["O"]] + [
                                          label2id[label_term] for label_term in self.data["label"][idx]
                                      ][:(self.args.max_seq_len - 2)] + [label2id["O"]]

            assert len(encoded_inputs["input_ids"]) == len(
                label), f"input_ids: {len(encoded_inputs['input_ids'])}, label: {len(label)}"
            return encoded_inputs["input_ids"], \
                   encoded_inputs["token_type_ids"], \
                   encoded_inputs["seq_len"], label

        return encoded_inputs["input_ids"], \
               encoded_inputs["token_type_ids"], \
               encoded_inputs["seq_len"]


def get_iter(args, phase, is_train):
    data = load_data(args.data_path + phase + ".txt")
    dataset = Extracion_Dataset(args, data, is_test=phase == "test")

    batchify_fn = lambda samples, fn=Tuple(
        Pad(axis=0, pad_val=args.tokenizer.pad_token_id, dtype="int64"),
        Pad(axis=0, pad_val=args.tokenizer.pad_token_type_id, dtype="int64"),
        Stack(dtype="int64"),
        Pad(axis=0, pad_val=-1, dtype="int64")
    ): fn(samples)
    batch_sampler = paddle.io.BatchSampler(dataset, batch_size=args.batch_size, shuffle=is_train)
    dataloader = DataLoader(dataset, batch_sampler=batch_sampler, collate_fn=batchify_fn)

    return dataloader
