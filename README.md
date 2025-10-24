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
tensorboard --logdir ./output/qwen2-7b-instruct-lora/sft
```

# 推理环境搭建
```
 conda create -n vllm0.11.0 python=3.10
pip install vllm==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu118
```