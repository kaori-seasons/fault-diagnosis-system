# 工业互联网故障诊断系统

## 📋 项目简介

这是一个基于 PaddleHub 的工业互联网故障诊断系统，能够自动分析工业设备故障文本，提取关键信息，并提供维护建议。

## 🚀 主要功能

- **智能文本分析**：使用 PaddleHub 的 LAC 模块进行词法分析
- **情感分析**：判断故障严重程度
- **实体识别**：自动识别设备名称、故障部位、技术术语等
- **知识库查询**：基于历史记录提供维护建议
- **Web API 服务**：提供 RESTful API 接口

## ⚠️ PaddleHub 安装问题分析

### 问题原因

1. **Python 版本兼容性**：PaddleHub 不支持 Python 3.12，建议使用 Python 3.7-3.10
2. **编译依赖失败**：`onnxoptimizer` 等 C++ 扩展编译失败
3. **系统架构问题**：macOS ARM64 架构可能存在兼容性问题
4. **依赖冲突**：paddlenlp 等依赖包版本冲突

### 解决方案

#### 方案一：使用 Python 3.10（推荐）

```bash
# 1. 删除当前虚拟环境
rm -rf .venv

# 2. 创建 Python 3.10 虚拟环境
python3.10 -m venv .venv

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

#### 方案二：手动安装兼容版本

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 安装基础依赖
pip install setuptools easydict colorama colorlog filelock tqdm pyzmq rarfile

# 3. 安装 PaddlePaddle（CPU 版本）
pip install paddlepaddle

# 4. 安装 PaddleHub
pip install paddlehub

# 5. 安装其他依赖
pip install -r requirements.txt
```

#### 方案三：使用 Docker（最稳定）

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8866
CMD ["python", "deploy_server.py"]
```

#### 方案四：简化版本（当前推荐）

由于 Python 3.12 兼容性问题，建议使用简化版本：

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 安装基础依赖
pip install flask pandas numpy jieba regex opencv-python pillow

# 3. 创建简化版本的故障诊断系统
# 使用 jieba 替代 PaddleHub 的 LAC 模块
# 使用简单的规则引擎替代深度学习模型
```

## 🔧 最新解决方案（2024年）

### 问题：paddlenlp 依赖冲突

当前遇到的主要问题是 `paddlenlp` 模块的依赖冲突。解决方案：

```bash
# 1. 安装缺失的依赖
pip install safetensors aistudio-sdk datasets dill multiprocess sentencepiece seqeval

# 2. 如果仍有问题，使用简化版本
pip install jieba scikit-learn
```

### 简化版本实现

如果 PaddleHub 安装仍有问题，可以使用简化版本：

```python
# 使用 jieba 替代 LAC
import jieba
import jieba.posseg as pseg

# 使用简单的规则引擎替代深度学习
def simple_entity_extraction(text):
    words = pseg.cut(text)
    entities = {
        'device_names': [],
        'fault_locations': [],
        'technical_terms': []
    }
    
    for word, flag in words:
        if 'n' in flag and any(keyword in word for keyword in ['机', '泵', '阀']):
            entities['device_names'].append(word)
        elif 'n' in flag and any(keyword in word for keyword in ['系统', '部位', '轴承']):
            entities['fault_locations'].append(word)
    
    return entities
```

## 📦 依赖说明

### 核心依赖
- `paddlehub>=2.3.1`：深度学习框架
- `paddlepaddle>=2.4.0`：PaddlePaddle 核心库

### Web 服务
- `flask>=2.0.0`：Web 框架
- `gunicorn>=20.1.0`：WSGI 服务器

### 数据处理
- `pandas>=1.3.0`：数据分析
- `numpy>=1.21.0`：数值计算

### NLP 处理
- `jieba>=0.42.1`：中文分词
- `regex>=2021.8.3`：正则表达式

### 其他工具
- `opencv-python>=4.5.0`：图像处理
- `sqlalchemy>=1.4.0`：数据库 ORM
- `loguru>=0.5.3`：日志记录

## 🛠️ 使用方法

### 1. 启动诊断系统

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行主程序
python industrial_fault_system.py
```

### 2. 启动 Web 服务

```bash
# 启动 Flask 服务
python deploy_server.py
```

服务将在 `http://localhost:8866` 启动

### 3. API 使用示例

```bash
curl -X POST http://localhost:8866/diagnose \
  -H "Content-Type: application/json" \
  -d '{"text": "检修员小明在5月5日9:00发现430号轧机制动力出现异常波动"}'
```

## 🔧 故障排除

### 常见问题

1. **PaddleHub 模块加载失败**
   - 检查 Python 版本是否为 3.7-3.10
   - 确保所有依赖已正确安装

2. **编译错误**
   - 在 macOS 上可能需要安装 Xcode Command Line Tools
   - 尝试使用预编译的 wheel 包

3. **内存不足**
   - 减少批处理大小
   - 使用 CPU 版本的 PaddlePaddle

4. **paddlenlp 依赖冲突**
   - 安装缺失的依赖：`pip install safetensors aistudio-sdk datasets`
   - 或使用简化版本替代

### 调试命令

```bash
# 检查 Python 版本
python --version

# 检查 PaddleHub 安装
python -c "import paddlehub; print(paddlehub.__version__)"

# 检查依赖
pip list | grep paddle
```

## 📝 项目结构

```
paddlehub-fault-diagnosis-system/
├── industrial_fault_system.py    # 主程序
├── deploy_server.py              # Web 服务
├── requirements.txt              # 依赖列表
├── .venv/                       # 虚拟环境
└── README.md                    # 项目说明
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题，请提交 Issue 或联系项目维护者。 