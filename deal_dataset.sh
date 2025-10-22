mkdir data

cp ./datasets/output_instruction_train.jsonl data/
cp ./datasets/output_instruction_dev.jsonl data/

# 创建正确的 dataset_info.json
cat > data/dataset_info.json << 'EOF'
{
  "output_instruction_train": {
    "file_name": "output_instruction_train.jsonl",
    "formatting": "alpaca"
  },
  "output_instruction_dev": {
    "file_name": "output_instruction_dev.jsonl",
    "formatting": "alpaca"
  }
}
EOF

echo "数据集已准备好，位于 data/ 目录下。"