# Chat_with_Datawhale 项目分阶段实现指导

## 阶段一：环境搭建与基础配置

### 1.1 项目目录结构搭建
- 按照文档中的目录结构创建所有必要的文件夹
- 初始化每个模块的`__init__.py`文件

### 1.2 环境依赖配置
- 安装Python 3.9+环境
- 使用uv创建虚拟环境：
  ```bash
  uv venv chat_with_datawhale --python 3.9
  ```
- 激活虚拟环境并安装依赖：
  ```bash
  # Windows
  chat_with_datawhale\Scripts\activate
  # Linux/Mac
  source chat_with_datawhale/bin/activate
  
  uv pip install -r requirements.txt
  ```

### 1.3 环境变量配置
- 在项目根目录创建`.env`文件
- 配置所有必需的API密钥和访问令牌

## 阶段二：知识库构建模块实现

### 2.1 GitHub仓库信息获取
- 实现`database/test_get_all_repo.py`
- 使用GitHub API获取Datawhale组织所有仓库的README文件
- 自动保存到`database/readme_db`目录
- 添加错误处理和批量处理功能

### 2.2 README文件摘要生成
- 实现`database/text_summary_readme.py`
- 读取README文件内容
- 过滤URL和敏感词汇
- 调用LLM生成简洁摘要（200字以内）
- 将摘要文件保存到`knowledge_db/readme_summary`

### 2.3 知识库文档加载
- 实现`database/create_db.py`
- 支持PDF、Markdown、TXT等多种格式
- 使用RecursiveCharacterTextSplitter进行文档切分
- 设置chunk_size=500, chunk_overlap=150
- 创建并持久化向量数据库（Chroma）

## 阶段三：Embedding模块实现

### 3.1 Embedding调用接口
- 实现`embedding/call_embedding.py`
- 集成本地m3e模型（moka-ai/m3e-base）
- 实现OpenAI和智谱AI的Embedding API接口
- 提供统一的调用接口支持模型切换

### 3.2 智谱AI Embedding封装
- 实现`embedding/zhipuai_embedding.py`
- 完整封装智谱AI Embedding接口
- 确保与LangChain框架兼容
- 支持批量文本嵌入处理

## 阶段四：LLM调用模块实现

### 4.1 通用LLM调用接口
- 实现`llm/call_llm.py`
- 建立统一的API密钥解析机制
- 实现多模型配置管理
- 集成环境变量自动加载

### 4.2 各厂商LLM封装
- 实现基础模块`llm/self_llm.py`（基础LLM抽象类）
- 实现`llm/spark_llm.py`（讯飞星火模型）
- 实现`llm/wenxin_llm.py`（百度文心一言模型）
- 实现`llm/zhipuai_llm.py`（智谱AI模型）
- 确保支持所有指定的模型版本

## 阶段五：问答链模块实现

### 5.1 模型到LLM的映射
- 实现`qa_chain/model_to_llm.py`
- 根据模型名称自动调用对应的LLM实例
- 支持所有集成的LLM模型
- 提供统一的参数配置接口

### 5.2 向量数据库获取
- 实现`qa_chain/get_vectordb.py`
- 实现向量数据库加载和初始化功能
- 支持本地持久化数据库
- 集成多种embedding模型
- 优化相似性检索效率

### 5.3 问答链实现
- 实现基础问答链`qa_chain/QA_chain_self.py`
  - 基于RetrievalQA的标准问答链
  - 支持自定义prompt模板
  - 实现源文档引用返回
  - 可配置检索参数
- 实现带历史记录的问答链`qa_chain/Chat_QA_chain_self.py`
  - 基于ConversationalRetrievalChain
  - 维护对话历史上下文
  - 支持历史记录长度控制
  - 实现历史记录清空和管理功能

## 阶段六：服务接口实现

### 6.1 API接口实现
- 实现`serve/api.py`
- 使用FastAPI构建RESTful API
- 实现问答接口和历史记录管理
- 支持多种请求格式
- 完善错误处理机制

### 6.2 Gradio界面实现
- 实现`serve/run_gradio.py`
- 构建用户友好的Web界面
- 实现实时问答交互
- 提供模型选择和参数配置
- 显示对话历史

## 阶段七：系统测试与部署

### 7.1 系统测试
- 编写并执行各模块单元测试
- 进行系统集成测试
- 验证API接口功能
- 测试Gradio界面交互

### 7.2 知识库构建
- 运行`database/test_get_all_repo.py`获取仓库README
- 运行`database/text_summary_readme.py`生成摘要
- 运行`database/create_db.py`构建向量数据库

### 7.3 服务启动
- 启动API服务：
  ```bash
  cd serve
  python api.py
  ```
- 启动Gradio界面：
  ```bash
  cd serve
  python run_gradio.py
  ```

## 阶段八：优化与扩展

### 8.1 性能优化
- 实现检索结果缓存机制
- 优化文档切分策略提升检索精度
- 增加检索结果重排序算法

### 8.2 功能增强
- 支持用户自定义知识库上传
- 增加更多文件格式支持（Word、Excel等）
- 实现多语言支持

### 8.3 长期规划
- 集成图像和视频内容理解
- 添加用户权限管理系统
- 实现分布式部署方案
- 开发移动端应用

## 验收标准

1. 所有模块功能正常运行
2. 通过所有单元测试和集成测试
3. API接口响应正常
4. Gradio界面交互流畅
5. 知识库内容完整准确
6. 系统文档齐全

## 注意事项

1. 严格按照项目架构组织代码
2. 遵循代码规范和注释要求
3. 及时提交代码并编写提交说明
4. 遇到问题及时沟通解决
5. 定期进行代码审查和优化

这个分阶段实现指导详细列出了每个阶段的任务和实现要点，帮助开发团队按部就班地完成项目开发。