# Chat_with_Datawhale 项目需求文档

## 1. 项目概述

本项目是一个基于大语言模型和RAG（检索增强生成）技术的个人知识库助手，专门为回答关于Datawhale开源项目的问题而设计。该系统能够通过自然语言查询快速检索相关知识并生成准确答案。

## 2. 核心功能模块

### 2.1 知识库构建模块

#### 功能描述
- 从GitHub Datawhale组织获取所有仓库的README文件
- 自动生成README内容摘要
- 加载知识文档并构建向量数据库

#### 技术要求
- 使用GitHub API获取仓库信息
- 实现文本摘要生成功能
- 支持多种文档格式（PDF、Markdown、TXT等）
- 使用Chroma作为向量数据库

#### 输入输出
- 输入：GitHub仓库URL列表
- 输出：存储在`knowledge_db/`目录中的摘要文件和`vector_db/`中的向量数据库

### 2.2 Embedding模块

#### 功能描述
- 将文本转换为向量表示
- 支持多种Embedding模型

#### 技术要求
- 本地m3e模型支持（moka-ai/m3e-base）
- OpenAI Embedding API接口
- 智谱AI Embedding API接口
- 统一调用接口，支持模型切换

#### 输入输出
- 输入：文本内容
- 输出：对应的向量表示

### 2.3 LLM调用模块

#### 功能描述
- 封装各大厂商的LLM接口
- 提供统一的调用接口

#### 技术要求
- 支持OpenAI、智谱AI、讯飞星火、百度文心等模型
- 实现API密钥管理和模型配置
- 提供模型到LLM的映射功能

#### 输入输出
- 输入：用户查询、上下文信息
- 输出：生成的回答文本

### 2.4 问答链模块

#### 功能描述
- 实现基于检索的问答流程
- 支持会话历史记录管理

#### 技术要求
- 基础问答链（RetrievalQA）
- 带历史记录的问答链（ConversationalRetrievalChain）
- 自定义prompt模板
- 可配置检索参数

#### 输入输出
- 输入：用户问题、可选的对话历史
- 输出：回答文本及源文档引用

### 2.5 服务接口模块

#### 功能描述
- 提供API和Web界面两种交互方式

#### 技术要求
- FastAPI构建的RESTful API
- Gradio用户界面
- 支持多种请求格式和参数配置
- 完整的错误处理机制

#### 输入输出
- 输入：HTTP请求或Web界面输入
- 输出：JSON格式响应或Web界面显示

## 3. 系统架构

```
Chat_with_Datawhale/
├── database/           # 数据库相关模块
│   ├── test_get_all_repo.py    # 获取仓库README
│   ├── text_summary_readme.py  # 生成README摘要
│   └── create_db.py            # 构建向量数据库
├── embedding/          # 向量嵌入模块
│   ├── call_embedding.py       # 统一调用接口
│   └── zhipuai_embedding.py    # 智谱AI封装
├── llm/               # 大语言模型封装
│   ├── call_llm.py             # 统一调用接口
│   ├── self_llm.py             # 基础抽象类
│   ├── spark_llm.py            # 讯飞星火模型
│   ├── wenxin_llm.py           # 百度文心一言模型
│   └── zhipuai_llm.py          # 智谱AI模型
├── qa_chain/          # 问答链实现
│   ├── model_to_llm.py         # 模型到LLM映射
│   ├── get_vectordb.py         # 获取向量数据库
│   ├── QA_chain_self.py        # 基础问答链
│   └── Chat_QA_chain_self.py   # 带历史记录问答链
├── serve/             # 服务层（API/Gradio）
│   ├── api.py                  # FastAPI接口
│   └── run_gradio.py           # Gradio界面
├── knowledge_db/      # 知识库文件
├── vector_db/         # 向量数据库
└── figures/           # 图片资源
```

## 4. 技术栈

- Python 3.9+
- FastAPI（API服务）
- Gradio（Web界面）
- LangChain（LLM和RAG框架）
- Chroma（向量数据库）
- uv（依赖管理）

## 5. 部署要求

### 5.1 环境依赖
- Python 3.9+
- 4GB+ RAM
- 网络连接（用于API调用）

### 5.2 环境变量配置
需要在项目根目录创建`.env`文件，包含以下内容：
```
OPENAI_API_KEY=your_openai_api_key
ZHIPUAI_API_KEY=your_zhipuai_api_key
WENXIN_API_KEY=your_wenxin_api_key
WENXIN_SECRET_KEY=your_wenxin_secret_key
SPARK_API_KEY=your_spark_api_key
SPARK_APPID=your_spark_appid
SPARK_API_SECRET=your_spark_api_secret
TOKEN=your_github_token
```

### 5.3 部署步骤

1. 克隆项目
2. 创建uv环境和安装依赖
3. 配置环境变量
4. 启动服务（API或Gradio界面）

## 6. 扩展规划

### 6.1 短期优化
- 实现检索结果缓存机制
- 优化文档切分策略提升检索精度
- 增加检索结果重排序算法

### 6.2 功能增强
- 支持用户自定义知识库上传
- 增加更多文件格式支持（Word、Excel等）
- 实现多语言支持

### 6.3 长期规划
- 集成图像和视频内容理解
- 添加用户权限管理系统
- 实现分布式部署方案
- 开发移动端应用

## 7. 测试要求

- 各模块单元测试通过
- 系统集成测试完成
- API接口功能验证
- Gradio界面交互测试

## 8. 性能指标

- 知识库包含88+个Datawhale开源项目
- 支持12个主流LLM模型
- 支持PDF、Markdown、TXT、视频字幕等多种文件格式
- 响应时间应控制在合理范围内（根据具体环境而定）

## 9. 维护要求

- 定期更新知识库内容
- 监控系统运行状态
- 及时修复发现的问题
- 根据用户反馈持续优化功能