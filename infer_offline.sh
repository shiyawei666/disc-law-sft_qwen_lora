#!/bin/bash

# test_inference.sh

export MODEL_NAME_OR_PATH="/data/nfs/models/qwen2.5-7b-instruct-awq"
export ADAPTER_PATH="./qwen_finetuned_optimized_20251024_161444"  # 替换为您的训练输出目录
export TEST_DATASET="./data/output_instruction_test.jsonl"  # 您的测试数据集名称
export OUTPUT_DIR="./test_results_$(date +%Y%m%d_%H%M%S)"

echo "开始测试集推理..."
echo "模型路径: $MODEL_NAME_OR_PATH"
echo "适配器路径: $ADAPTER_PATH"
echo "测试数据集: $TEST_DATASET"
echo "输出目录: $OUTPUT_DIR"

# 直接使用llamafactory的eval功能
CUDA_VISIBLE_DEVICES=3 llamafactory-cli eval \
    --model_name_or_path $MODEL_NAME_OR_PATH \
    --adapter_name_or_path $ADAPTER_PATH \
    --template qwen \
    --dataset $TEST_DATASET \
    --dataset_dir ./data \
    --finetuning_type lora \
    --output_dir $OUTPUT_DIR \
    --per_device_eval_batch_size 4 \
    --max_new_tokens 512 \
    --predict_with_generate true \
    --metric_for_best_model eval_bleu-4 \
    --do_predict true \
    --overwrite_cache

echo "测试完成！结果保存在: $OUTPUT_DIR"