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

## 操作流程介绍

![Alt text](<./static/截屏2023-09-20 12.03.17.png>)

### 界面简介
ChatDoc由控制区和聊天对话区组成。控制区用于管理文档和知识库，聊天对话区用于输入消息接受消息。

上图中的10号区域是ChatDoc当前选中的文档，若10号区域为空，即ChatDoc没有选中任何文档，而此时仍在聊天对话区与ChatDoc对话，只是此时的ChatDoc是一个单纯依托ChatGLM2的ChatBot。

### 上传文档
点击`1`选择要上传的文档，然后点击按钮`4`构建知识库。随后将embedding文档，完成后将被选中，并显示在10号区域，接着就可开始对话。我们可重复上传文档，embedding成功的文档均会进入10号区域。

### 持久化知识库
10号区域选中的文档在用户刷新或者关闭页面时，将会清空，而如何能保存这些已经embedding的文档，我们可以持久化知识库，在下次进入无需embedding计算即可加载知识库。具体做法是，在10号区域不为空的情况下，点击按钮`5`即可持久化知识库，知识库的名称是所有文档名称以逗号连接而成。

### 导入知识库

进入ChatDoc我们可以从选择框`2`查看目前以持久化的知识库，选中我们需要加载的知识库后，点击按钮`3`导入知识库。完成后即可开始对话。

### 删除知识库

当我们需要删除本地已经持久化的知识库时，我们可从选择框`2`选择我们要删除的知识库，然后点击按钮`6`删除知识库。

### 重命名知识库

![Alt text](<./static/截屏2023-09-20 15.47.08.png>)

由于知识库的命名是由其文档的名称组合而来，难免造成知识库名称过长的问题，ChatDoc提供了一个修改知识库名称的功能，选择框`2`选择我们要修改的知识库，然后点击按钮`9`重命名知识库，随后ChatDoc将弹出一个输入框和一个确认按钮，如上图。在输出框输入我们修改至的名称，然后点击确认重命名按钮。

### 清楚聊天记录

点击按钮`7`即可清楚聊天对话区聊天记录。其他不受影响。

### 移除选中文档

点击按钮`8`将清空10号区域，同时清楚聊天记录。