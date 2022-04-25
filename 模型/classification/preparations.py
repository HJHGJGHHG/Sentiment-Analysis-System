import json
import paddle
import random
import numpy as np
from tqdm import tqdm
from collections import defaultdict
from paddle.io import Dataset, DataLoader
from paddlenlp.data import Pad, Stack, Tuple

label2id = {'负向': 0, '正向': 1}
id2label = {0: '负向', 1: '正向'}


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    paddle.seed(seed)


def load_data(data_path):
    with open(data_path, "r", encoding="utf-8") as f:
        data = {
            "label": [],
            "aspect_text": [],
            "text": []
        }
        for line in f.readlines():
            items = line.strip().split("\t")
            assert len(items) == 3
            data["label"].append(int(items[0]))
            data["aspect_text"].append(items[1])
            data["text"].append(items[2])
            
            return data


class Classification_Dataset(Dataset):
    def __init__(self, args, data, is_test=False):
        super(Classification_Dataset, self).__init__()
        self.args = args
        self.data = data  # {'id': [], 'aspect': [], 'opinions': [], 'text': [], 'aspect_text': []}
        self.tokenizer = args.tokenizer
        self.is_test = is_test
    
    def __len__(self):
        return len(self.data["text"])
    
    def __getitem__(self, idx):
        return self._convert_to_tensors(idx)
    
    def _convert_to_tensors(self, idx):
        encoded_inputs = self.args.tokenizer(
            self.data["aspect_text"][idx],
            text_pair=self.data["text"][idx],
            max_seq_len=self.args.max_seq_len,
            return_length=True)
        
        if not self.is_test:
            label = self.data["label"][idx]
            return encoded_inputs["input_ids"], encoded_inputs[
                "token_type_ids"], encoded_inputs["seq_len"], label
        
        return encoded_inputs["input_ids"], encoded_inputs[
            "token_type_ids"], encoded_inputs["seq_len"]


def get_iter(args, phase, is_train):
    data = load_data(args.data_path + phase + ".txt")
    dataset = Classification_Dataset(args, data, is_test=phase == "test")
    
    batchify_fn = lambda samples, fn=Tuple(
        Pad(axis=0, pad_val=args.tokenizer.pad_token_id, dtype="int64"),
        Pad(axis=0, pad_val=args.tokenizer.pad_token_type_id, dtype="int64"),
        Stack(dtype="int64"),
        Stack(dtype="int64")
    ): fn(samples)
    batch_sampler = paddle.io.BatchSampler(dataset, batch_size=args.batch_size, shuffle=is_train)
    dataloader = DataLoader(dataset, batch_sampler=batch_sampler, collate_fn=batchify_fn)
    
    return dataloader
