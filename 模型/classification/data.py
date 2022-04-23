import json
from tqdm import tqdm
label_dict = ({'负向': 0, '正向': 1}, {0: '负向', 1: '正向'})

def load_dict(dict_path):
    with open(dict_path, "r", encoding="utf-8") as f:
        words = [word.strip() for word in f.readlines()]
        word2id = dict(zip(words, range(len(words))))
        id2word = dict((v, k) for k, v in word2id.items())

        return word2id, id2word


def read(data_path):
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            items = line.strip().split("\t")
            assert len(items) == 3
            example = {
                "label": int(items[0]),
                "aspect_text": items[1],
                "text": items[2]
            }

            yield example


def convert_example_to_feature(example,
                               tokenizer,
                               label2id,
                               max_seq_len=512,
                               is_test=False):
    encoded_inputs = tokenizer(
        example["aspect_text"],
        text_pair=example["text"],
        max_seq_len=max_seq_len,
        return_length=True)

    if not is_test:
        label = example["label"]
        return encoded_inputs["input_ids"], encoded_inputs[
            "token_type_ids"], encoded_inputs["seq_len"], label

    return encoded_inputs["input_ids"], encoded_inputs[
        "token_type_ids"], encoded_inputs["seq_len"]
