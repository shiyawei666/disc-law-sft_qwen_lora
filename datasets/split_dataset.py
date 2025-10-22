#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import argparse
import os


def split_dataset(input_file: str, dev_ratio: float = 0.2, seed: int = 42):
    """
    随机分割数据集为训练集和验证集

    Args:
        input_file: 输入JSONL文件路径
        dev_ratio: 验证集比例 (0-1)
        seed: 随机种子
    """

    # 设置随机种子保证可重复性
    random.seed(seed)

    # 读取所有数据
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_count = len(lines)
    print(f"📊 总数据量: {total_count} 行")

    # 随机打乱数据
    shuffled_lines = lines.copy()
    random.shuffle(shuffled_lines)

    # 计算分割点
    split_index = int(total_count * (1 - dev_ratio))
    train_lines = shuffled_lines[:split_index]
    dev_lines = shuffled_lines[split_index:]

    print(f"🎯 分割比例: {dev_ratio * 100}% 作为验证集")
    print(f"📚 训练集: {len(train_lines)} 行")
    print(f"🧪 验证集: {len(dev_lines)} 行")

    # 生成输出文件名
    base_name = os.path.splitext(input_file)[0]
    train_file = f"{base_name}_train.jsonl"
    dev_file = f"{base_name}_dev.jsonl"

    # 保存训练集
    with open(train_file, 'w', encoding='utf-8') as f:
        f.writelines(train_lines)

    # 保存验证集
    with open(dev_file, 'w', encoding='utf-8') as f:
        f.writelines(dev_lines)

    print(f"💾 训练集保存至: {train_file}")
    print(f"💾 验证集保存至: {dev_file}")

    # 预览样本
    print("\n📖 训练集样本预览:")
    for i, line in enumerate(train_lines[:2]):
        data = json.loads(line.strip())
        print(
            f"  样本 {i + 1}: {json.dumps(data, ensure_ascii=False)[:100]}...")

    print("\n📖 验证集样本预览:")
    for i, line in enumerate(dev_lines[:2]):
        data = json.loads(line.strip())
        print(
            f"  样本 {i + 1}: {json.dumps(data, ensure_ascii=False)[:100]}...")

    return train_file, dev_file


def main():
    parser = argparse.ArgumentParser(description='随机分割数据集')
    parser.add_argument('--input', '-i', required=True,
                        help='输入JSONL文件路径')
    parser.add_argument('--ratio', '-r', type=float, default=0.2,
                        help='验证集比例 (默认: 0.2)')
    parser.add_argument('--seed', '-s', type=int, default=42,
                        help='随机种子 (默认: 42)')

    args = parser.parse_args()

    print("🚀 开始随机分割数据集...")
    split_dataset(args.input, args.ratio, args.seed)
    print("✅ 分割完成!")


if __name__ == "__main__":
    main()