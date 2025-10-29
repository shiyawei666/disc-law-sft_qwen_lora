#!/bin/bash

export MODEL_NAME_OR_PATH=/data/nfs/models/qwen2.5-7b-instruct
export OUTPUT_DIR="./qwen_finetuned_optimized_$(date +%Y%m%d_%H%M%S)"

echo "开始优化单卡训练..."
echo "输出目录: $OUTPUT_DIR"
echo "TensorBoard日志: $OUTPUT_DIR/runs"

CUDA_VISIBLE_DEVICES=3 llamafactory-cli train \
    --model_name_or_path $MODEL_NAME_OR_PATH \
    --template qwen \
    --stage sft \
    --dataset output_instruction_train \
    --dataset_dir ./data \
    --output_dir $OUTPUT_DIR \
    --finetuning_type lora \
    --lora_rank 8 \
    --lora_target q_proj,v_proj \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 8 \
    --learning_rate 2e-4 \
    --num_train_epochs 3 \
    --quantization_bit 4 \
    --gradient_checkpointing true \
    --fp16 \
    --do_train true \
    --do_eval true \
    --eval_strategy epoch \
    --eval_dataset output_instruction_dev \
    --predict_with_generate true \
    --max_new_tokens 256 \
    --per_device_eval_batch_size 4 \
    --metric_for_best_model eval_bleu-4 \
    --logging_steps 10 \
    --load_best_model_at_end \
    --save_total_limit 2 \
    --save_strategy epoch \
    --overwrite_cache \
    --report_to tensorboard \
    --logging_dir "$OUTPUT_DIR/runs" \
    --log_level info \
    --run_name "qwen_finetune_$(date +%Y%m%d)" \
    --save_safetensors true \
    --export_dir "$OUTPUT_DIR/merged_model" \
    --export_size 2 \
    --export_device cpu \
    --export_legacy_format false

echo "训练完成！"
echo "启动TensorBoard查看训练过程:"
echo "tensorboard --logdir $OUTPUT_DIR/runs --host 0.0.0.0 --port 6006"
