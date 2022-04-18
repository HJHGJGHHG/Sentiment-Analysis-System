import os
import paddle
import argparse
from paddlenlp.transformers import SkepForTokenClassification, SkepForSequenceClassification

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_type", type=str, default="extraction", choices=["extraction", "classification"],
                        help="The model type that you wanna export.")
    parser.add_argument("--original_model_path", type=str, default='/root/autodl-tmp/SAS/模型/checkpoint/original_model',
                        help="The path of original model path that you want to load.")
    parser.add_argument("--ext_model_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/extraction/best_ext.pdparams',
                        help="The path of extraction model path that you want to load.")
    parser.add_argument("--cls_model_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/classification/best_cls.pdparams',
                        help="The path of classification model path that you want to load.")
    
    parser.add_argument("--ext_save_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/extraction/static',
                        help="The path of the exported static extraction model.")
    parser.add_argument("--cls_save_path", type=str,
                        default='/root/autodl-tmp/SAS/模型/checkpoint/classification/static',
                        help="The path of the exported static classification model.")
    args = parser.parse_args()
    
    # load model with saved state_dict
    if args.model_type == "extraction":
        model = SkepForTokenClassification.from_pretrained(args.original_model_path, num_classes=5)
        loaded_state_dict = paddle.load(args.ext_model_path)
        model.load_dict(loaded_state_dict)
        print(f"Loaded parameters from {args.ext_model_path}")
    else:
        model = SkepForSequenceClassification.from_pretrained(args.original_model_path, num_classes=2)
        loaded_state_dict = paddle.load(args.cls_model_path)
        model.load_dict(loaded_state_dict)
        print(f"Loaded parameters from {args.cls_model_path}")
    
    model.eval()
    # convert to static graph with specific input description
    model = paddle.jit.to_static(
        model,
        input_spec=[
            paddle.static.InputSpec(
                shape=[None, None], dtype="int64"),  # input_ids
            paddle.static.InputSpec(
                shape=[None, None], dtype="int64")  # token_type_ids
        ])
    
    # save to static model
    if args.model_type == "extraction":
        paddle.jit.save(model, args.ext_save_path)
        print(f"static {args.model_type} model has been to {args.ext_save_path}")
    else:
        paddle.jit.save(model, args.cls_save_path)
        print(f"static {args.model_type} model has been to {args.cls_save_path}")
