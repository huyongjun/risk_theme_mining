#!/bin/bash

# 指定你的预训练模型位置
export BERT_BASE_DIR=./google预训练-chinese_L-12_H-768_A-12
# 指定你的输入数据的目录（该目录下，放着前面的三个文件train.tsv, dev.tsv, test.tsv）
export MY_DATASET=./data
##指定你的模型输出目录
export OUTPUT_PATH=./output
export TASK_NAME=senti

nohup python run_classifier.py \
  --data_dir=$MY_DATASET \
  --task_name=$TASK_NAME \
  --output_dir=$OUTPUT_PATH \
  --vocab_file=$BERT_BASE_DIR/vocab.txt \
  --init_checkpoint=$BERT_BASE_DIR/bert_model.ckpt \
  --bert_config_file=$BERT_BASE_DIR/bert_config.json \
  --do_train=True \
  --do_eval=True \
  --do_predict=True \
  --max_seq_length=128 \
  --train_batch_size=16 \
  --learning_rate=5e-5 \
  --num_train_epochs=2.0 \
  >train.log 2>&1 &