#!/bin/bash

export ADAPTER_PATH="$(pwd)/qwen_finetuned_optimized_20251028_124521"
export BASE_MODEL=/data/nfs/models/qwen2.5-7b-instruct

echo "使用动态加载方式启动（不合并）..."
echo "基础模型: $BASE_MODEL"
echo "适配器路径: $ADAPTER_PATH"

CUDA_VISIBLE_DEVICES=0,1,2,3 python -m vllm.entrypoints.openai.api_server \
    --model $BASE_MODEL \
    --enable-lora \
    --lora-modules my-lora=$ADAPTER_PATH \
    --served-model-name qwen2.5-7b-instruct-qlora \
    --trust-remote-code \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.6 \
    --max-model-len 1024 \
    --block-size 16 \
    --max-num-batched-tokens 1024 \
    --max-num-seqs 2 \
    --swap-space 16 \
    --port 8000