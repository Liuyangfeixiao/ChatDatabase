"""
README文件摘要生成器
功能：
1. 读取database/readme_db目录下的README文件
2. 过滤URL和敏感词汇
3. 调用LLM生成简洁摘要（200字以内）
4. 将摘要文件保存到knowledge_db/readme_summary目录
"""

import os
import re
import json
import logging
import markdown
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from openai import OpenAI
from zhipuai import ZhipuAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup

@dataclass
class ReadmeInfo:
    """README文件信息"""
    repo_name: str
    file_path: str
    content: str
    metadata: Dict


class ReadmeSummarizer:
    """README文件摘要生成器"""
    
    def __init__(self, llm_type: str = "openai", api_key: Optional[str] = None):
        """
        初始化摘要生成器
        
        Args:
            llm_type: LLM类型，支持 "zhipuai", "openai"
            api_key: API密钥，如果为None则从.env文件获取
        """
        # 加载.env文件
        load_dotenv()
        
        self.llm_type = llm_type
        self.setup_logging()
        self.setup_llm(api_key)
        
        # 设置路径
        self.readme_db_path = Path("database/readme_db")
        self.summary_output_path = Path("knowledge_db/readme_summary")
        self.summary_output_path.mkdir(parents=True, exist_ok=True)
        
        # URL过滤正则表达式
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # 敏感词汇列表（可根据需要扩展）
        self.sensitive_words = [
            "密码", "password", "token", "secret", "key", "私钥", "访问令牌",
            "api_key", "access_token", "private_key", "秘钥"
        ]
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_llm(self, api_key: Optional[str]):
        """设置LLM客户端"""
        if self.llm_type == "zhipuai":
            api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
            if not api_key:
                raise ValueError("请在.env文件中设置ZHIPUAI_API_KEY或传入api_key参数")
            self.client = ZhipuAI(api_key=api_key)
        elif self.llm_type == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("请在.env文件中设置OPENAI_API_KEY或传入api_key参数")
            self.client = OpenAI(api_key=api_key,
                                 base_url="https://api.chatanywhere.tech/v1")
    
    def filter_content(self, content: str) -> str:
        """
        过滤内容中的URL和敏感词汇
        
        Args:
            content: 原始内容
            
        Returns:
            过滤后的内容
        """
        # 过滤URL
        filtered_content = self.url_pattern.sub('[URL]', content)
        
        # 过滤敏感词汇
        for word in self.sensitive_words:
            filtered_content = re.sub(
                re.escape(word), 
                '[敏感信息]', 
                filtered_content, 
                flags=re.IGNORECASE
            )
        
        return filtered_content
    
    def generate_summary_zhipuai(self, content: str) -> str:
        """
        使用智谱AI生成摘要
        
        Args:
            content: 待摘要的内容
            
        Returns:
            生成的摘要
        """
        prompt = f"""
请为以下README内容生成一个简洁的摘要，要求：
1. 摘要长度不超过200字
2. 提炼项目的核心内容
3. 使用中文输出
4. 保持专业性和准确性

README内容：
{content}

请生成摘要：
"""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"智谱AI调用失败: {e}")
            return f"摘要生成失败: {str(e)}"
    
    def generate_summary_openai(self, content: str) -> str:
        """
        使用OpenAI生成摘要
        
        Args:
            content: 待摘要的内容
            
        Returns:
            生成的摘要
        """
        prompt = f"""
请为以下README内容生成一个简洁的摘要，要求：
1. 摘要长度不超过200字
2. 提炼项目的核心内容
3. 使用中文输出
4. 保持专业性和准确性

README内容：
{content}

请生成摘要：
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"OpenAI调用失败: {e}")
            return f"摘要生成失败: {str(e)}"
    
    def generate_summary(self, content: str) -> str:
        """
        生成摘要
        
        Args:
            content: 待摘要的内容
            
        Returns:
            生成的摘要
        """
        if self.llm_type == "zhipuai":
            return self.generate_summary_zhipuai(content)
        elif self.llm_type == "openai":
            return self.generate_summary_openai(content)
        else:
            raise ValueError(f"不支持的LLM类型: {self.llm_type}")
    
    def read_readme_files(self) -> List[ReadmeInfo]:
        """
        读取所有README文件
        
        Returns:
            README文件信息列表
        """
        readme_files = []
        
        if not self.readme_db_path.exists():
            self.logger.error(f"README数据库路径不存在: {self.readme_db_path}")
            return readme_files
        
        for repo_dir in self.readme_db_path.iterdir():
            if repo_dir.is_dir():
                readme_path = repo_dir / "README.md"
                if readme_path.exists():
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取元数据（前几行的仓库信息）
                        metadata = self.extract_metadata(content)
                        # 需要将md文件转换为html文件进行提取
                        html = markdown.markdown(content)
                        # Use BeautifulSoup to extract text
                        soup = BeautifulSoup(html, 'html.parser')
                        readme_files.append(ReadmeInfo(
                            repo_name=repo_dir.name,
                            file_path=str(readme_path),
                            content=soup.get_text(),
                            metadata=metadata
                        ))
                        
                    except Exception as e:
                        self.logger.error(f"读取README文件失败 {readme_path}: {e}")
        
        self.logger.info(f"成功读取 {len(readme_files)} 个README文件")
        return readme_files
    
    def extract_metadata(self, content: str) -> Dict:
        """
        从README内容中提取元数据
        
        Args:
            content: README内容
            
        Returns:
            元数据字典
        """
        metadata = {}
        lines = content.split('\n')
        
        for line in lines[:20]:  # 只检查前20行
            if '仓库描述' in line:
                metadata['description'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif '仓库地址' in line:
                metadata['url'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif '创建时间' in line:
                metadata['created_at'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif '更新时间' in line:
                metadata['updated_at'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif '主要语言' in line:
                metadata['language'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif 'Star数' in line:
                metadata['stars'] = line.split(':', 1)[1].strip() if ':' in line else ''
        
        return metadata
    
    def save_summary(self, repo_name: str, summary: str, metadata: Dict):
        """
        保存摘要到文件
        
        Args:
            repo_name: 仓库名称
            summary: 摘要内容
            metadata: 元数据
        """
        summary_data = {
            "repo_name": repo_name,
            "summary": summary,
            "metadata": metadata,
            "generated_at": str(Path().resolve()),
            "llm_type": self.llm_type
        }
        
        output_file = self.summary_output_path / f"{repo_name}_summary.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"摘要已保存: {output_file}")
            
        except Exception as e:
            self.logger.error(f"保存摘要失败 {output_file}: {e}")
    
    def process_all_readmes(self):
        """
        处理所有README文件，生成摘要
        """
        self.logger.info("开始处理README文件摘要生成...")
        
        # 读取所有README文件
        readme_files = self.read_readme_files()
        
        if not readme_files:
            self.logger.warning("没有找到README文件")
            return
        
        # 处理每个README文件
        success_count = 0
        for readme_info in readme_files:
            try:
                self.logger.info(f"正在处理: {readme_info.repo_name}")
                
                # 过滤内容
                filtered_content = self.filter_content(readme_info.content)
                
                # 生成摘要
                summary = self.generate_summary(filtered_content)
                
                # 保存摘要
                self.save_summary(readme_info.repo_name, summary, readme_info.metadata)
                
                success_count += 1
                
            except Exception as e:
                self.logger.error(f"处理 {readme_info.repo_name} 失败: {e}")
        
        self.logger.info(f"摘要生成完成! 成功处理 {success_count}/{len(readme_files)} 个文件")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="README文件摘要生成器")
    parser.add_argument(
        "--llm-type", 
        choices=["zhipuai", "openai"], 
        default="openai",
        help="LLM类型"
    )
    parser.add_argument(
        "--api-key",
        help="API密钥"
    )
    
    args = parser.parse_args()
    
    try:
        summarizer = ReadmeSummarizer(
            llm_type=args.llm_type,
            api_key=args.api_key
        )
        summarizer.process_all_readmes()
        
    except Exception as e:
        logging.error(f"程序执行失败: {e}")


if __name__ == "__main__":
    main()