#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse


def convert_to_instruction_format(input_file: str, output_file: str):
    """
    将JSONL文件转换为指令格式（instruction-input-output）

    Args:
        input_file: 输入JSONL文件路径
        output_file: 输出JSONL文件路径
    """

    converted_data = []
    success_count = 0
    error_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # 解析原始数据
                original_data = json.loads(line)

                # 构建指令格式
                instruction_format = {
                    "instruction": original_data.get('input', ''),
                    "input": "",  # 输入字段为空，因为instruction已经包含完整问题
                    "output": original_data.get('output', '')
                }

                # 验证必要字段
                if not instruction_format["instruction"] or not \
                instruction_format["output"]:
                    print(f"⚠️  第 {line_num} 行缺少必要字段，已跳过")
                    error_count += 1
                    continue

                converted_data.append(instruction_format)
                success_count += 1
                print(f"✓ 成功转换第 {line_num} 行数据")

            except json.JSONDecodeError as e:
                print(f"✗ 第 {line_num} 行JSON解析错误: {e}")
                error_count += 1
                continue
            except Exception as e:
                print(f"✗ 第 {line_num} 行处理错误: {e}")
                error_count += 1
                continue

    # 保存转换后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"\n🎉 转换完成！")
    print(f"📊 成功转换: {success_count} 条数据")
    print(f"❌ 失败数量: {error_count} 条")
    print(f"💾 输出文件: {output_file}")

    return converted_data


def preview_samples(output_file: str, num_samples: int = 3):
    """
    预览转换后的数据样本
    """
    print(f"\n📖 预览前 {num_samples} 条转换后的数据:")
    print("=" * 60)

    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= num_samples:
                    break
                data = json.loads(line.strip())
                print(f"样本 {i + 1}:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                print("-" * 50)
    except Exception as e:
        print(f"预览失败: {e}")


def validate_output_format(output_file: str):
    """
    验证输出格式是否正确
    """
    print(f"\n🔍 验证输出格式...")

    required_fields = ["instruction", "input", "output"]
    valid_count = 0
    total_count = 0

    with open(output_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            total_count += 1
            try:
                data = json.loads(line.strip())

                # 检查必要字段
                missing_fields = [field for field in required_fields if
                                  field not in data]
                if missing_fields:
                    print(f"❌ 第 {line_num} 行缺少字段: {missing_fields}")
                    continue

                # 检查字段类型
                if not isinstance(data["instruction"], str) or not isinstance(
                        data["output"], str):
                    print(f"❌ 第 {line_num} 行字段类型错误")
                    continue

                valid_count += 1

            except Exception as e:
                print(f"❌ 第 {line_num} 行验证失败: {e}")
                continue

    print(f"✅ 格式验证完成: {valid_count}/{total_count} 条数据有效")


def main():
    parser = argparse.ArgumentParser(description='JSONL文件转换为指令格式')
    parser.add_argument('--input', '-i', required=True,
                        help='输入JSONL文件路径')
    parser.add_argument('--output', '-o', required=True,
                        help='输出JSONL文件路径')
    parser.add_argument('--preview', '-p', action='store_true',
                        help='转换后预览数据样本')
    parser.add_argument('--validate', '-v', action='store_true',
                        help='验证输出格式')

    args = parser.parse_args()

    print("🚀 开始转换JSONL文件为指令格式...")
    print(f"📁 输入文件: {args.input}")
    print(f"📁 输出文件: {args.output}")

    # 执行转换
    converted_data = convert_to_instruction_format(args.input, args.output)

    if args.preview and converted_data:
        preview_samples(args.output)

    if args.validate:
        validate_output_format(args.output)


if __name__ == "__main__":
    main()