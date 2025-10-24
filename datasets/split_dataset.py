#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import argparse
import os


def split_dataset(input_file: str, ratios: tuple = (0.8, 0.1, 0.1),
                  seed: int = 42):
    """
    随机分割数据集为训练集、验证集和测试集

    Args:
        input_file: 输入JSONL文件路径
        ratios: 分割比例 (train_ratio, dev_ratio, test_ratio)，默认为(0.8, 0.1, 0.1)
        seed: 随机种子
    """

    # 验证比例参数
    if len(ratios) != 3:
        raise ValueError(
            "比例参数必须包含三个值: (train_ratio, dev_ratio, test_ratio)")

    train_ratio, dev_ratio, test_ratio = ratios
    total_ratio = train_ratio + dev_ratio + test_ratio

    if abs(total_ratio - 1.0) > 0.001:  # 允许浮点数误差
        raise ValueError(f"比例之和必须为1.0，当前为: {total_ratio}")

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
    train_end = int(total_count * train_ratio)
    dev_end = train_end + int(total_count * dev_ratio)

    train_lines = shuffled_lines[:train_end]
    dev_lines = shuffled_lines[train_end:dev_end]
    test_lines = shuffled_lines[dev_end:]

    # 打印分割结果
    print(
        f"🎯 分割比例: 训练集 {train_ratio * 100}% | 验证集 {dev_ratio * 100}% | 测试集 {test_ratio * 100}%")
    print(f"📚 训练集: {len(train_lines)} 行")
    print(f"🧪 验证集: {len(dev_lines)} 行")
    print(f"🔬 测试集: {len(test_lines)} 行")

    # 生成输出文件名
    base_name = os.path.splitext(input_file)[0]
    train_file = f"{base_name}_train.jsonl"
    dev_file = f"{base_name}_dev.jsonl"
    test_file = f"{base_name}_test.jsonl"

    # 保存数据集
    with open(train_file, 'w', encoding='utf-8') as f:
        f.writelines(train_lines)

    with open(dev_file, 'w', encoding='utf-8') as f:
        f.writelines(dev_lines)

    with open(test_file, 'w', encoding='utf-8') as f:
        f.writelines(test_lines)

    print(f"💾 训练集保存至: {train_file}")
    print(f"💾 验证集保存至: {dev_file}")
    print(f"💾 测试集保存至: {test_file}")

    # 预览样本
    def preview_samples(dataset_name, lines, count=2):
        print(f"\n📖 {dataset_name}样本预览:")
        for i, line in enumerate(lines[:count]):
            try:
                data = json.loads(line.strip())
                preview = json.dumps(data, ensure_ascii=False)
                if len(preview) > 100:
                    preview = preview[:100] + "..."
                print(f"  样本 {i + 1}: {preview}")
            except:
                print(f"  样本 {i + 1}: [无法解析JSON]")

    preview_samples("训练集", train_lines)
    preview_samples("验证集", dev_lines)
    preview_samples("测试集", test_lines)

    return train_file, dev_file, test_file


def main():
    parser = argparse.ArgumentParser(
        description='随机分割数据集为训练集、验证集和测试集')
    parser.add_argument('--input', '-i', required=True,
                        help='输入JSONL文件路径')
    parser.add_argument('--ratios', '-r', type=float, nargs=3,
                        default=[0.8, 0.1, 0.1],
                        help='分割比例: train_ratio dev_ratio test_ratio (默认: 0.8 0.1 0.1)')
    parser.add_argument('--seed', '-s', type=int, default=42,
                        help='随机种子 (默认: 42)')

    args = parser.parse_args()

    print("🚀 开始随机分割数据集...")
    print(f"📁 输入文件: {args.input}")
    print(
        f"⚖️  分割比例: 训练集 {args.ratios[0] * 100}% | 验证集 {args.ratios[1] * 100}% | 测试集 {args.ratios[2] * 100}%")

    try:
        train_file, dev_file, test_file = split_dataset(args.input,
                                                        tuple(args.ratios),
                                                        args.seed)
        print("✅ 分割完成!")
        print(f"📊 最终结果:")
        print(f"  训练集: {train_file}")
        print(f"  验证集: {dev_file}")
        print(f"  测试集: {test_file}")
    except Exception as e:
        print(f"❌ 分割失败: {e}")


if __name__ == "__main__":
    main()