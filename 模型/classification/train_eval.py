import paddle
import logging
import paddle.nn.functional as F

from paddlenlp.metrics.glue import AccuracyAndF1
from paddlenlp.transformers import SkepTokenizer, SkepForSequenceClassification, LinearDecayWithWarmup

from preparations import set_seed, get_iter, label2id

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("classification_train.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_args_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="../checkpoint/original_model")
    parser.add_argument("--num_epochs", type=int, default=3, help="Number of epoches for training.")
    parser.add_argument("--data_path", type=str, default="../data/cls_data/", help="The path of data.")
    parser.add_argument("--batch_size", type=int, default=16, help="Total examples' number in batch for training.")
    parser.add_argument("--max_seq_len", type=int, default=512, help="Batch size per GPU/CPU for training.")
    parser.add_argument("--learning_rate", type=float, default=3e-5, help="The initial learning rate for optimizer.")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay rate for L2 regularizer.")
    parser.add_argument("--max_grad_norm", type=float, default=1.0, help="Max grad norm to clip gradient.")
    parser.add_argument("--warmup_proportion", type=float, default=0.1,
                        help="Linear warmup proption over the training process.")
    parser.add_argument("--log_steps", type=int, default=50, help="Frequency of printing log.")
    parser.add_argument("--eval_steps", type=int, default=500, help="Frequency of performing evaluation.")
    parser.add_argument("--seed", type=int, default=1234, help="Random seed for initialization.")
    parser.add_argument('--device', choices=['cpu', 'gpu'], default="gpu",
                        help="Select which device to train model, defaults to gpu.")
    parser.add_argument("--checkpoints", type=str, default=None, help="Directory to save checkpoint.")
    parser.add_argument("--load_model_dir", type=str, default=None)

    parser.add_argument("--test_only", type=bool, default=True, help="Only test the model.")
    return parser


def evaluate(model, dev_iter, metric):
    model.eval()
    metric.reset()
    with paddle.no_grad():
        for batch in dev_iter:
            input_ids, token_type_ids, _, labels = batch
            logits = model(input_ids, token_type_ids=token_type_ids)
            correct = metric.compute(logits, labels)
            metric.update(correct)

    accuracy, precision, recall, f1, _ = metric.accumulate()

    return accuracy, precision, recall, f1


def train_model(args, model, train_iter, dev_iter, lr_scheduler, optimizer, metric):
    global_step, best_f1 = 1, 0.
    model.train()
    for epoch in range(1, args.num_epochs + 1):
        for batch in train_iter():
            input_ids, token_type_ids, _, labels = batch
            # logits: batch_size, seql_len, num_tags
            logits = model(input_ids, token_type_ids=token_type_ids)
            loss = F.cross_entropy(logits, labels)

            loss.backward()
            lr_scheduler.step()
            optimizer.step()
            optimizer.clear_grad()

            if global_step > 0 and global_step % args.log_steps == 0:
                logger.info(
                    f"epoch: {epoch} - global_step: {global_step}/{len(train_iter) * args.num_epochs} - loss:{loss.numpy().item():.6f}"
                )
            if (global_step > 0 and global_step % args.eval_steps == 0) or global_step == len(
                    train_iter) * args.num_epochs:
                accuracy, precision, recall, f1 = evaluate(model, dev_iter, metric)
                model.train()
                if f1 > best_f1:
                    logger.info(
                        f"best F1 performence has been updated: {best_f1:.5f} --> {f1:.5f}"
                    )
                    best_f1 = f1
                    if args.checkpoints is not None:
                        paddle.save(model.state_dict(), f"{args.checkpoints}/best.pdparams")
                logger.info(
                    f'evalution result: accuracy:{accuracy:.5f} precision: {precision:.5f}, recall: {recall:.5f},  F1: {f1:.5f}'
                )

            global_step += 1


def main(args):
    tokenizer = SkepTokenizer.from_pretrained(args.model_path)
    args.tokenizer = tokenizer

    train_iter = get_iter(args, phase="train", is_train=True)
    dev_iter = get_iter(args, phase="dev", is_train=False)
    test_iter = get_iter(args, phase="test", is_train=False)

    model = SkepForSequenceClassification.from_pretrained(args.model_path, num_classes=len(label2id))
    if args.load_model_dir is not None:
        model.load_dict(paddle.load(args.load_model_dir))

    lr_scheduler = LinearDecayWithWarmup(
        learning_rate=args.learning_rate,
        total_steps=len(train_iter) * args.num_epochs,
        warmup=args.warmup_proportion)
    decay_params = [
        p.name for n, p in model.named_parameters()
        if not any(nd in n for nd in ["bias", "norm"])
    ]
    grad_clip = paddle.nn.ClipGradByGlobalNorm(args.max_grad_norm)
    optimizer = paddle.optimizer.AdamW(
        learning_rate=lr_scheduler,
        parameters=model.parameters(),
        weight_decay=args.weight_decay,
        apply_decay_param_fun=lambda x: x in decay_params,
        grad_clip=grad_clip)

    metric = AccuracyAndF1()

    if not args.test_only:
        train_model(args, model, train_iter, dev_iter, lr_scheduler, optimizer, metric)
    else:
        accuracy, precision, recall, f1 = evaluate(model, dev_iter, metric)
        logger.info(
            f'dev result: accuracy:{accuracy:.5f} precision: {precision:.5f}, recall: {recall:.5f},  F1: {f1:.5f}')


if __name__ == "__main__":
    args = get_args_parser().parse_args()
    set_seed(args.seed)
    main(args)
