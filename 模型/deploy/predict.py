import json
import paddle
import pickle as pkl

from paddle.io import DataLoader
from collections import defaultdict
from paddlenlp.data import Pad, Stack, Tuple
from seqeval.metrics.sequence_labeling import get_entities
from paddlenlp.transformers import SkepTokenizer, SkepForTokenClassification, SkepForSequenceClassification

import sys

sys.path.append("/root/autodl-tmp/SAS/模型")
from extraction.preparations import Extracion_Dataset, set_seed
from classification.preparations import Classification_Dataset

ext_id2label = {0: 'O', 1: 'B-Aspect', 2: 'I-Aspect', 3: 'B-Opinion', 4: 'I-Opinion'}
ext_label2id = {'O': 0, 'B-Aspect': 1, 'I-Aspect': 2, 'B-Opinion': 3, 'I-Opinion': 4}
cls_label2id = {'负向': 0, '正向': 1}
cls_id2label = {0: '负向', 1: '正向'}


def concate_aspect_and_opinion(text, aspect, opinions):
    aspect_text = ""
    for opinion in opinions:
        if text.find(aspect) <= text.find(opinion):
            aspect_text += aspect + opinion + "，"
        else:
            aspect_text += opinion + aspect + "，"
    aspect_text = aspect_text[:-1]
    
    return aspect_text


def decoding(text, tag_seq):
    assert len(text) == len(
        tag_seq), f"text len: {len(text)}, tag_seq len: {len(tag_seq)}"
    
    puncs = list(",.?;!，。？；！")
    splits = [idx for idx in range(len(text)) if text[idx] in puncs]
    
    prev = 0
    sub_texts, sub_tag_seqs = [], []
    for i, split in enumerate(splits):
        sub_tag_seqs.append(tag_seq[prev:split])
        sub_texts.append(text[prev:split])
        prev = split
    sub_tag_seqs.append(tag_seq[prev:])
    sub_texts.append((text[prev:]))
    
    ents_list = []
    for sub_text, sub_tag_seq in zip(sub_texts, sub_tag_seqs):
        ents = get_entities(sub_tag_seq, suffix=False)
        ents_list.append((sub_text, ents))
    
    aps = []
    no_a_words = []
    for sub_tag_seq, ent_list in ents_list:
        sub_aps = []
        sub_no_a_words = []
        for ent in ent_list:
            ent_name, start, end = ent
            if ent_name == "Aspect":
                aspect = sub_tag_seq[start:end + 1]
                sub_aps.append([aspect])
                if len(sub_no_a_words) > 0:
                    sub_aps[-1].extend(sub_no_a_words)
                    sub_no_a_words.clear()
            else:
                ent_name == "Opinion"
                opinion = sub_tag_seq[start:end + 1]
                if len(sub_aps) > 0:
                    sub_aps[-1].append(opinion)
                else:
                    sub_no_a_words.append(opinion)
        
        if sub_aps:
            aps.extend(sub_aps)
            if len(no_a_words) > 0:
                aps[-1].extend(no_a_words)
                no_a_words.clear()
        elif sub_no_a_words:
            if len(aps) > 0:
                aps[-1].extend(sub_no_a_words)
            else:
                no_a_words.extend(sub_no_a_words)
    
    if no_a_words:
        no_a_words.insert(0, "None")
        aps.append(no_a_words)
    
    return aps


def get_ext_iter(args, is_static=False):
    # load data
    if args.from_database:
        data = pkl.load(open(args.bin_path, "rb"))  # {"id": [], "text": []}
    else:
        with open(args.data_path, "r", encoding="utf-8") as f:
            data = {"text": []}
            for text in f.readlines():
                text = text[:-1] if text[-1] == "\n" else text
                text = list(text)
                data["text"].append(text)
    
    ext_dataset = Extracion_Dataset(args, data, is_test=True)
    if args.from_database:
        batchify_fn = lambda samples, fn=Tuple(
            Pad(axis=0, pad_val=args.tokenizer.pad_token_id, dtype="int64"),
            Pad(axis=0, pad_val=args.tokenizer.pad_token_type_id, dtype="int64"),
            Stack(dtype="int64"),
            Stack(dtype="int64"),  # 评论ID
        ): fn(samples)
    else:
        batchify_fn = lambda samples, fn=Tuple(
            Pad(axis=0, pad_val=args.tokenizer.pad_token_id, dtype="int64"),
            Pad(axis=0, pad_val=args.tokenizer.pad_token_type_id, dtype="int64"),
            Stack(dtype="int64"),
        ): fn(samples)
    batch_sampler = paddle.io.BatchSampler(ext_dataset, batch_size=args.batch_size, shuffle=False)
    ext_iter = DataLoader(ext_dataset, batch_sampler=batch_sampler, collate_fn=batchify_fn)
    if is_static:
        return ext_dataset, batchify_fn
    return ext_iter, ext_dataset


def predict_ext(args):
    ext_iter, ext_dataset = get_ext_iter(args)
    
    # load ext model
    ext_state_dict = paddle.load(args.ext_model_path)
    ext_model = SkepForTokenClassification.from_pretrained(args.original_model_path, num_classes=len(ext_label2id))
    ext_model.load_dict(ext_state_dict)
    print("extraction model loaded.")
    
    ext_model.eval()
    results = {
        "id": [],
        "aspect": [],
        "opinions": [],
        "text": [],
        "aspect_text": []
    }
    for bid, batch in enumerate(ext_iter):
        print(bid * args.batch_size)
        if args.from_database:
            input_ids, token_type_ids, seq_lens, comment_id = batch
        else:
            input_ids, token_type_ids, seq_lens = batch
        logits = ext_model(input_ids, token_type_ids=token_type_ids)
        
        predictions = logits.argmax(axis=2).numpy()
        for eid, (seq_len, prediction) in enumerate(zip(seq_lens, predictions)):
            idx = bid * args.batch_size + eid
            tag_seq = [ext_id2label[idx] for idx in prediction[:seq_len][1:-1]]
            text = ''.join(ext_dataset.data['text'][idx])
            aps = decoding(text[:args.max_seq_len - 2], tag_seq)
            for aid, ap in enumerate(aps):
                if len(ap) == 1:
                    continue
                aspect, opinions = ''.join(ap[0]), [''.join(x) for x in list(set([tuple(item) for item in ap[1:]]))]
                if aspect == "None" or len(aspect) == 1:
                    continue
                aspect_text = concate_aspect_and_opinion(text, aspect, opinions)
                if args.from_database:
                    results["id"].append(str(comment_id.numpy()[eid]) + "_" + str(aid))
                else:
                    results["id"].append(str(idx) + "_" + str(aid))
                results["aspect"].append(aspect)
                results["opinions"].append(opinions)
                results["text"].append(text)
                results["aspect_text"].append(aspect_text)
    print("predicting with extraction model done!")
    return results


def get_cls_iter(args, ext_results, is_static=False):
    cls_dataset = Classification_Dataset(args, ext_results, is_test=True)
    batchify_fn = lambda samples, fn=Tuple(
        Pad(axis=0, pad_val=args.tokenizer.pad_token_id, dtype="int64"),
        Pad(axis=0, pad_val=args.tokenizer.pad_token_type_id, dtype="int64"),
        Stack(dtype="int64"),
    ): fn(samples)
    batch_sampler = paddle.io.BatchSampler(cls_dataset, batch_size=args.batch_size, shuffle=False)
    cls_iter = DataLoader(cls_dataset, batch_sampler=batch_sampler, collate_fn=batchify_fn)
    if is_static:
        return cls_dataset, batchify_fn
    return cls_iter, cls_dataset


def predict_cls(args, ext_results):
    paddle.device.cuda.empty_cache()
    cls_iter, cls_dataset = get_cls_iter(args, ext_results)
    cls_state_dict = paddle.load(args.cls_model_path)
    cls_model = SkepForSequenceClassification.from_pretrained(args.original_model_path, num_classes=len(cls_label2id))
    cls_model.load_dict(cls_state_dict)
    print("classification model loaded.")
    
    cls_model.eval()
    results = []
    for bid, batch in enumerate(cls_iter):
        input_ids, token_type_ids, seq_lens = batch
        logits = cls_model(input_ids, token_type_ids=token_type_ids)
        
        predictions = logits.argmax(axis=1).numpy().tolist()
        results.extend(predictions)
    
    results = [cls_id2label[pred_id] for pred_id in results]
    print("predicting with classification model done!")
    return results


def post_process(args, ext_results, cls_results):
    paddle.device.cuda.empty_cache()
    assert len(ext_results["aspect_text"]) == len(cls_results)
    
    collect_dict = defaultdict(list)
    for i in range(len(cls_results)):
        ext_result = {
            "id": ext_results["id"][i],
            "aspect": ext_results["aspect"][i],
            "opinions": ext_results["opinions"][i],
            "text": ext_results["text"][i],
            "aspect_text": ext_results["aspect_text"][i],
            "sentiment_polarity": cls_results[i]
        }
        eid, _ = ext_results["id"][i].split("_")
        collect_dict[eid].append(ext_result)
    
    sentiment_results = []
    for eid in collect_dict.keys():
        sentiment_result = {}
        ap_list = []
        for idx, single_ap in enumerate(collect_dict[eid]):
            sentiment_result["comment_id"] = eid
            if idx == 0:
                sentiment_result["text"] = single_ap["text"]
            ap_list.append({
                "aspect": single_ap["aspect"],
                "opinions": single_ap["opinions"],
                "sentiment_polarity": single_ap["sentiment_polarity"]
            })
        sentiment_result["ap_list"] = ap_list
        sentiment_results.append(sentiment_result)
    
    with open(args.save_path, "w", encoding="utf-8") as f:
        for sentiment_result in sentiment_results:
            f.write(json.dumps(sentiment_result, ensure_ascii=False) + "\n")


def get_args_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--original_model_path", type=str, default='/root/autodl-tmp/SAS/模型/checkpoint/original_model',
                        help="The path of original model path that you want to load.")
    parser.add_argument("--ext_model_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/extraction/best_ext.pdparams',
                        help="The path of extraction model path that you want to load.")
    parser.add_argument("--cls_model_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/classification/best_cls.pdparams',
                        help="The path of classification model path that you want to load.")
    parser.add_argument('--data_path', type=str, default='/root/autodl-tmp/SAS/模型/data/comments/beaf.txt',
                        help="The path of test set that you want to predict.")
    parser.add_argument('--bin_path', type=str, default='/root/autodl-tmp/SAS/模型/data/new_comments.pkl')
    parser.add_argument('--save_path', type=str, default='/root/autodl-tmp/SAS/模型/data/result.json',
                        help="The saving path of predict results.")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size per GPU/CPU for training.")
    parser.add_argument("--max_seq_len", type=int, default=512,
                        help="The maximum total input sequence length after tokenization.")
    parser.add_argument("--seed", type=int, default=1234, help="Random seed for initialization.")
    parser.add_argument("--from_database", type=bool, default=True, help="Load data from database.")
    return parser


if __name__ == '__main__':
    args = get_args_parser().parse_args()
    set_seed(args.seed)
    args.tokenizer = SkepTokenizer.from_pretrained(args.original_model_path)
    ext_results = predict_ext(args)
    cls_results = predict_cls(args, ext_results)
    
    post_process(args, ext_results, cls_results)
    print(f"sentiment analysis results has been saved to path: {args.save_path}")
