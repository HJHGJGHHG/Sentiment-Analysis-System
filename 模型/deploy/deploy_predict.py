import os
import json
import paddle

from paddle import inference
from collections import defaultdict
from paddlenlp.transformers import SkepTokenizer

import sys

sys.path.append("../")
from extraction.preparations import set_seed
from predict import get_ext_iter, get_cls_iter, decoding, concate_aspect_and_opinion

ext_id2label = {0: 'O', 1: 'B-Aspect', 2: 'I-Aspect', 3: 'B-Opinion', 4: 'I-Opinion'}
ext_label2id = {'O': 0, 'B-Aspect': 1, 'I-Aspect': 2, 'B-Opinion': 3, 'I-Opinion': 4}
cls_label2id = {'负向': 0, '正向': 1}
cls_id2label = {0: '负向', 1: '正向'}


class Predictor(object):
    def __init__(self, args):
        self.args = args
        self.ext_predictor, self.ext_input_handles, self.ext_output_hanle = self.create_predictor(
            args.ext_model_path)
        print(f"ext_model_path: {args.ext_model_path}, {self.ext_predictor}")
        self.cls_predictor, self.cls_input_handles, self.cls_output_hanle = self.create_predictor(
            args.cls_model_path)
        print(f"cls_model_path: {args.cls_model_path}, {self.cls_predictor}")
        self.tokenizer = SkepTokenizer.from_pretrained(args.original_model_path)
    
    def create_predictor(self, model_path):
        model_file = model_path + ".pdmodel"
        params_file = model_path + ".pdiparams"
        if not os.path.exists(model_file):
            raise ValueError("not find model file path {}".format(model_file))
        if not os.path.exists(params_file):
            raise ValueError("not find params file path {}".format(params_file))
        config = paddle.inference.Config(model_file, params_file)
        
        if self.args.device == "gpu":
            # set GPU configs accordingly
            # such as intialize the gpu memory, enable tensorrt
            config.enable_use_gpu(100, 0)
            precision_map = {
                "fp16": inference.PrecisionType.Half,
                "fp32": inference.PrecisionType.Float32,
                "int8": inference.PrecisionType.Int8
            }
            precision_mode = precision_map[args.precision]
            
            if args.use_tensorrt:
                config.enable_tensorrt_engine(
                    max_batch_size=self.args.batch_size,
                    min_subgraph_size=30,
                    precision_mode=precision_mode)
        else:  # CPU
            # set CPU configs accordingly,
            # such as enable_mkldnn, set_cpu_math_library_num_threads
            config.disable_gpu()
            if args.enable_mkldnn:
                # cache 10 different shapes for mkldnn to avoid memory leak
                config.set_mkldnn_cache_capacity(10)
                config.enable_mkldnn()
            config.set_cpu_math_library_num_threads(args.cpu_threads)
        
        config.switch_use_feed_fetch_ops(False)
        predictor = paddle.inference.create_predictor(config)
        input_handles = [
            predictor.get_input_handle(name)
            for name in predictor.get_input_names()
        ]
        output_handle = predictor.get_output_handle(predictor.get_output_names()
                                                    [0])
        
        return predictor, input_handles, output_handle
    
    def predict_ext(self, args):
        ext_dataset, batchify_fn = get_ext_iter(args, is_static=True)
        batch_list = [
            [ext_dataset[i] for i in range(idx, idx + args.batch_size) if i < len(ext_dataset)]
            for idx in range(0, len(ext_dataset), args.batch_size)
        ]
        
        results = {
            "id": [],
            "aspect": [],
            "opinions": [],
            "text": [],
            "aspect_text": []
        }
        for bid, batch in enumerate(batch_list):
            input_ids, token_type_ids, seq_lens = batchify_fn(batch)
            self.ext_input_handles[0].copy_from_cpu(input_ids)
            self.ext_input_handles[1].copy_from_cpu(token_type_ids)
            self.ext_predictor.run()
            logits = self.ext_output_hanle.copy_to_cpu()
            
            predictions = logits.argmax(axis=2)
            for eid, (seq_len, prediction) in enumerate(zip(seq_lens, predictions)):
                idx = bid * args.batch_size + eid
                tag_seq = [ext_id2label[idx] for idx in prediction[:seq_len][1:-1]]
                text = ''.join(ext_dataset.data['text'][idx])
                aps = decoding(text[:args.max_seq_len - 2], tag_seq)
                for aid, ap in enumerate(aps):
                    if len(ap) == 1:
                        continue
                    aspect, opinions = ''.join(ap[0]), [''.join(x) for x in list(set([tuple(item) for item in ap[1:]]))]
                    aspect_text = concate_aspect_and_opinion(text, aspect, opinions)
                    results["id"].append(str(idx) + "_" + str(aid))
                    results["aspect"].append(aspect)
                    results["opinions"].append(opinions)
                    results["text"].append(text)
                    results["aspect_text"].append(aspect_text)
        print("predicting with extraction model done!")
        return results
    
    def predict_cls(self, args, ext_results):
        paddle.device.cuda.empty_cache()
        cls_dataset, batchify_fn = get_cls_iter(args, ext_results, is_static=True)
        batch_list = [
            [cls_dataset[i] for i in range(idx, idx + args.batch_size) if i < len(cls_dataset)]
            for idx in range(0, len(cls_dataset), args.batch_size)
        ]
        
        results = []
        for batch in batch_list:
            input_ids, token_type_ids, _ = batchify_fn(batch)
            self.cls_input_handles[0].copy_from_cpu(input_ids)
            self.cls_input_handles[1].copy_from_cpu(token_type_ids)
            self.cls_predictor.run()
            logits = self.cls_output_hanle.copy_to_cpu()
            
            predictions = logits.argmax(axis=1).tolist()
            results.extend(predictions)
        print("predicting with classification model done!")
        return results
    
    def post_process(self, args, ext_results, cls_results):
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
                "sentiment_polarity": cls_id2label[cls_results[i]]
            }
            eid, _ = ext_results["id"][i].split("_")
            collect_dict[eid].append(ext_result)
        
        sentiment_results = []
        for eid in collect_dict.keys():
            sentiment_result = {}
            ap_list = []
            for idx, single_ap in enumerate(collect_dict[eid]):
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
    
    def predict(self):
        ext_results = self.predict_ext(self.args)
        cls_results = self.predict_cls(self.args, ext_results)
        self.post_process(self.args, ext_results, cls_results)


def get_args_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--original_model_path", type=str, default='/root/autodl-tmp/SAS/模型/checkpoint/original_model',
                        help="The path of original model path that you want to load.")
    parser.add_argument("--ext_model_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/extraction/static',
                        help="The path of extraction model path that you want to load.")
    parser.add_argument("--cls_model_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/classification/static',
                        help="The path of classification model path that you want to load.")
    parser.add_argument('--data_path', type=str, default='/root/autodl-tmp/SAS/模型/data/comments.txt',
                        help="The path of test set that you want to predict.")
    parser.add_argument('--save_path', type=str, default='/root/autodl-tmp/SAS/模型/data/deploy_result.json',
                        help="The saving path of predict results.")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size per GPU/CPU for training.")
    parser.add_argument("--max_seq_len", type=int, default=512,
                        help="The maximum total input sequence length after tokenization.")
    parser.add_argument("--seed", type=int, default=1234, help="Random seed for initialization.")
    parser.add_argument("--use_tensorrt", action='store_true', help="Whether to use inference engin TensorRT.")
    parser.add_argument("--precision", default="fp32", type=str, choices=["fp32", "fp16", "int8"],
                        help='The tensorrt precision.')
    parser.add_argument("--device", default="gpu", choices=["gpu", "cpu"], help="Device selected for inference.")
    parser.add_argument('--cpu_threads', default=10, type=int, help='Number of threads to predict when using cpu.')
    parser.add_argument('--enable_mkldnn', default=False, type=eval, choices=[True, False],
                        help='Enable to use mkldnn to speed up when using cpu.')
    return parser


if __name__ == '__main__':
    args = get_args_parser().parse_args()
    set_seed(args.seed)
    args.tokenizer = SkepTokenizer.from_pretrained(args.original_model_path)
    
    predictor = Predictor(args)
    predictor.predict()
