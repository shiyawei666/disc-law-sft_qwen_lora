# 数据集
[数据集](https://huggingface.co/datasets/ShengbinYue/DISC-Law-SFT)

# 安装python虚拟环境, 并激活
```
conda create -n llamafactory python=3.10
conda activate llamafactory
```
# 安装部署llamafactory
```
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
git checkout -b v0.9.3 tags/v0.9.3
pip install -e ".[torch,metrics]" --no-build-isolation
```

# 训练过程中监控指标
```
tensorboard --logdir qwen_finetuned_optimized_20251028_162602/runs --host 0.0.0.0 --port 6006
```
<img width="1883" height="894" alt="image" src="https://github.com/user-attachments/assets/22b5a1bf-53e1-4f7c-8a68-ceed2dfedd9e" />


# 合并lora微调后的模型
```
使用merge.sh脚本进行合并，报错
Traceback (most recent call last):
  File "/data/miniconda3/envs/llamafactory/bin/llamafactory-cli", line 7, in <module>
    sys.exit(main())
  File "/data/workspaces/shiyawei/LLaMA-Factory/src/llamafactory/cli.py", line 151, in main
    COMMAND_MAP[command]()
  File "/data/workspaces/shiyawei/LLaMA-Factory/src/llamafactory/train/tuner.py", line 129, in export_model
    raise ValueError("Cannot merge adapters to a quantized model.")
ValueError: Cannot merge adapters to a quantized model.
模型合并失败，请检查错误信息

原因：LLaMA-Factory不允许将LoRA适配器合并到量化模型（AWQ模型）中，LoRA适配器只能合并到原始的全精度模型中。
```

# 推理环境搭建
```
 conda create -n vllm0.11.0 python=3.10
pip install vllm==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu118
```


# vllm推理微调后的模型
```
针对微调awq的模型无法合并的问题，使用vllm推理中的特殊参数：--lora-modules
```

# 使用gradio界面化体验模型推理性能
```
python infer_gradio_show.py
```
<img width="1841" height="863" alt="image" src="https://github.com/user-attachments/assets/e1cd814f-ad56-433c-8290-eb9286156140" />
<img width="1871" height="899" alt="image" src="https://github.com/user-attachments/assets/2ca7301a-b283-4569-95fe-508b262e0af7" />
<img width="1804" height="892" alt="image" src="https://github.com/user-attachments/assets/536d3e5d-672d-43ec-a731-091bf2eebb1a" />



# 经验
```
1. 不要去微调量化的模型，会很麻烦。
```
