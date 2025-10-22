
#!/bin/bash

export MODEL_NAME_OR_PATH=/data/nfs/models/qwen2.5-0.5B

echo "开始优化单卡训练（预计3-4小时）..."
CUDA_VISIBLE_DEVICES=3 llamafactory-cli train \
    --model_name_or_path $MODEL_NAME_OR_PATH \
    --template qwen \
    --dataset output_instruction_train \
    --dataset_dir ./data \
    --output_dir ./qwen_finetuned_optimized \
    --finetuning_type lora \
    --lora_rank 8 \
    --lora_target q_proj,v_proj \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 2 \
    --learning_rate 2e-4 \
    --num_train_epochs 2 \
    --fp16 \
    --eval_strategy steps \
    --eval_steps 100 \
    --eval_dataset output_instruction_dev \
    --metric_for_best_model eval_loss \
    --load_best_model_at_end \
    --predict_with_generate true \
    --max_new_tokens 512 \
    --save_steps 100 \
    --logging_steps 20 \
    --save_total_limit 2 \
    --overwrite_cache

echo "优化训练完成！"