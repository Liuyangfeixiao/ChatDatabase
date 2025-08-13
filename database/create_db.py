"""
Knowledge Base Document Loading Module
功能：
1. 支持PDF、Markdown、TXT等多种格式文档加载
2. 使用RecursiveCharacterTextSplitter进行文档切分
3. 设置chunk_size=500, chunk_overlap=150
4. 创建并持久化向量数据库（Chroma）
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tempfile
from pathlib import Path
from typing import List, Optional
import logging
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import (
    UnstructuredFileLoader,
    PyMuPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    JSONLoader
)
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_community.embeddings import OpenAIEmbeddings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "./knowledge_db"
DEFAULT_PERSIST_PATH = "./vector_db"

class KnowledgeBaseLoader:
    """知识库文档加载器"""
    
    def __init__(self, 
                 docs_path: str = DEFAULT_DB_PATH,
                 persist_path: str = DEFAULT_PERSIST_PATH,
                 chunk_size: int = 500,
                 chunk_overlap: int = 150):
        """
        初始化知识库加载器
        
        Args:
            docs_path: 文档路径
            persist_path: 向量数据库持久化路径
            chunk_size: 文档切分大小
            chunk_overlap: 文档重叠大小
        """
        self.docs_path = Path(docs_path)
        self.persist_path = Path(persist_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 创建持久化目录
        self.persist_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化文本分割器, "\n\n"分割段落
        # "/n"分割行
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(f"知识库加载器初始化完成")
        logger.info(f"文档路径: {self.docs_path}")
        logger.info(f"持久化路径: {self.persist_path}")
    
    def load_documents(self) -> List[Document]:
        """
        加载所有支持格式的文档
        
        Returns:
            文档列表
        """
        documents = []
        
        if not self.docs_path.exists():
            logger.error(f"文档路径不存在: {self.docs_path}")
            return documents
            
        # 遍历所有支持的文件类型
        supported_extensions = [".pdf", ".md", ".txt", ".json"]
        
        for file_path in self.docs_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    logger.info(f"正在加载文档: {file_path}")
                    docs = self._load_single_document(file_path)
                    documents.extend(docs)
                except Exception as e:
                    logger.error(f"加载文档失败 {file_path}: {e}")
                    continue
        
        logger.info(f"成功加载 {len(documents)} 个文档片段")
        return documents
    
    def _load_single_document(self, file_path: Path) -> List[Document]:
        """
        加载单个文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档列表
        """
        # 根据文件扩展名选择加载器
        if file_path.suffix.lower() == ".pdf":
            loader = PyMuPDFLoader(str(file_path))
        elif file_path.suffix.lower() == ".md":
            loader = UnstructuredMarkdownLoader(str(file_path))
        elif file_path.suffix.lower() == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
        elif file_path.suffix.lower() == ".json":
            loader = JSONLoader(str(file_path), jq_schema='.', text_content=False)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
        
        # 加载文档
        documents = loader.load()
        
        # 分割文档
        split_docs = self.text_splitter.split_documents(documents)
        
        # 添加元数据
        for doc in split_docs:
            doc.metadata["source"] = str(file_path)
            
        return split_docs
    
    def _get_llm_embedding(self, embedding_name="openai"):
        # 加载.env文件
        load_dotenv()
        OPENAI_URL = os.environ["OPENAI_API_BASE"]
        OPENAI_KEY = os.environ["OPENAI_API_KEY"]
        if embedding_name == "openai":
            return OpenAIEmbeddings(openai_api_base=OPENAI_URL,
                                    openai_api_key=OPENAI_KEY)
        

    
    def create_vector_db(self, 
                         embedding_function=None,
                         collection_name: str = "knowledge_db") -> Chroma:
        """
        创建向量数据库
        
        Args:
            embedding_function: 嵌入函数
            collection_name: 集合名称
            
        Returns:
            Chroma向量数据库实例
        """
        # 加载文档
        documents = self.load_documents()
        
        if not documents:
            logger.warning("没有加载到任何文档")
            raise ValueError(f"文档：{documents}")
        
        # 创建向量数据库
        logger.info("正在创建向量数据库...")
        vector_db = Chroma.from_documents(
            documents=documents,
            embedding=embedding_function,
            persist_directory=str(self.persist_path),
            collection_name=collection_name
        )
        
        # 持久化
        vector_db.persist()
        logger.info("向量数据库创建并持久化完成")
        
        return vector_db
    
    def load_existing_db(self, 
                         embedding_function=None,
                         collection_name: str = "knowledge_db") -> Chroma:
        """
        加载已有的向量数据库
        
        Args:
            embedding_function: 嵌入函数
            collection_name: 集合名称
            
        Returns:
            Chroma向量数据库实例
        """
        logger.info("正在加载现有向量数据库...")
        vector_db = Chroma(
            persist_directory=str(self.persist_path),
            embedding_function=embedding_function,
            collection_name=collection_name
        )
        logger.info("向量数据库加载完成")
        return vector_db


def main():
    """主函数"""
    try:
        # 创建知识库加载器
        loader = KnowledgeBaseLoader(
            docs_path="knowledge_db/readme_summary",
            persist_path="vector_db/chroma",
            chunk_size=500,
            chunk_overlap=150
        )
        
        # 创建OpenAI嵌入函数
        embeddings = loader._get_llm_embedding()
        
        # 创建向量数据库
        vector_db = loader.create_vector_db(embedding_function=embeddings)
        
        if vector_db:
            print("知识库向量数据库创建成功!")
            print(f"文档片段数量: {vector_db._collection.count()}")
        else:
            print("知识库向量数据库创建失败!")
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"错误: {e}")


if __name__ == "__main__":
    main()