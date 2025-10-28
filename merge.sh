#!/bin/bash

# 设置基础模型路径（与训练时相同）
export MODEL_NAME_OR_PATH=/data/nfs/models/qwen2.5-7b-instruct

# 设置要合并的适配器路径（请根据实际训练结果修改这个路径）
# 示例：export ADAPTER_PATH="./qwen_finetuned_optimized_20241201_143052"
export ADAPTER_PATH="./qwen_finetuned_optimized_20251028_124521"

# 设置合并后模型的输出目录
export MERGED_MODEL_DIR="${ADAPTER_PATH}/merged_model"

echo "开始合并LoRA适配器到基础模型..."
echo "基础模型: $MODEL_NAME_OR_PATH"
echo "适配器路径: $ADAPTER_PATH"
echo "合并后模型输出目录: $MERGED_MODEL_DIR"

# 检查适配器路径是否存在
if [ ! -d "$ADAPTER_PATH" ]; then
    echo "错误: 适配器路径不存在: $ADAPTER_PATH"
    echo "请确保路径正确，或修改 ADAPTER_PATH 变量"
    exit 1
fi

# 执行模型合并
CUDA_VISIBLE_DEVICES=3 llamafactory-cli export \
    --model_name_or_path $MODEL_NAME_OR_PATH \
    --adapter_name_or_path $ADAPTER_PATH \
    --template qwen \
    --finetuning_type lora \
    --export_dir $MERGED_MODEL_DIR \
    --export_size 2 \
    --export_device cpu \
    --export_legacy_format false

# 检查合并是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "模型合并完成！"
    echo "合并后的模型保存在: $MERGED_MODEL_DIR"
    echo ""
    echo "可以使用以下命令通过vLLM启动合并后的模型:"
    echo "python -m vllm.entrypoints.openai.api_server \\"
    echo "    --model $MERGED_MODEL_DIR \\"
    echo "    --served-model-name qwen-merged-model \\"
    echo "    --trust-remote-code \\"
    echo "    --gpu-memory-utilization 0.9 \\"
    echo "    --port 8000"
else
    echo "模型合并失败，请检查错误信息"
    exit 1
fi