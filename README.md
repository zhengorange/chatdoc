# ChatDoc

这个项目是基于[ChatGLM2-TPU](https://github.com/sophgo/ChatGLM2-TPU)实现的文档对话工具。项目可在BM1684X上独立部署运行。


## Introduction
该项目的主要目标是通过使用自然语言来简化与文档的交互，并提取有价值的信息。此项目使用LangChain和ChatGLM2构建，以向用户提供流畅自然的对话体验。

![](static/web-ui.png)


## Features

- 支持多种文档格式PDF, DOCX, PPTX, TXT等。
- 与文档内容进行聊天，提出问题根据文档获得相关答案。
- 用户友好的界面，确保流畅的交互。

## Architecture

![](./static/architecture.png)

## Installation

按照以下步骤，可以将这个项目部署到SoPhGo盒子上。

1. 克隆代码:
```bash
git clone https://github.com/zhengorange/chatdoc
```
2. 进入项目路径:
```bash
cd chatdoc
```
3. 按照依赖
```bash
pip install -r requirements.txt
```

## Configuration

项目加载需要配置两个模型文件的地址和一个库文件地址。

```ini
libtpuchat_path = ../chatglm/libtpuchat.so
bmodel_path = ../chatglm/chatglm2-6b.bmodel
token_path = ../chatglm/tokenizer.model
```

## Usage: Web by Streamlit


```bash
bash run.sh
```