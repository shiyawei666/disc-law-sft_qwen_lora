#python deal_dataset.py --input DISC-Law-SFT-Pair-QA-released.jsonl --output output_instruction.jsonl

python split_dataset.py --input output_instruction.jsonl --ratio 0.2