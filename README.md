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


# 数据集
[数据集](https://huggingface.co/datasets/ShengbinYue/DISC-Law-SFT)

