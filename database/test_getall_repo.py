import json
import requests
import os
import base64
import time
from loguru import logger
from dotenv import load_dotenv
from typing import List, Dict, Optional


class DatawhaleRepoCollector:
    """Datawhale组织仓库README收集器"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化收集器
        
        Args:
            token: GitHub访问令牌，如果不提供则从环境变量获取
        """
        load_dotenv()
        self.token = token or os.getenv('TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Please set TOKEN environment variable.")
            
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.org_name = 'datawhalechina'
        self.readme_dir = 'database/readme_db'
        
        # 创建README存储目录
        os.makedirs(self.readme_dir, exist_ok=True)
        
        # 配置日志
        logger.add("logs/repo_collector.log", rotation="1 MB")
    
    def get_organization_repos(self) -> List[Dict]:
        """
        获取Datawhale组织的所有仓库列表
        
        Returns:
            仓库信息列表
        """
        repos = []
        page = 1
        per_page = 100
        
        logger.info(f"开始获取{self.org_name}组织的仓库列表")
        
        while True:
            try:
                url = f"{self.base_url}/orgs/{self.org_name}/repos"
                params = {
                    'page': page,
                    'per_page': per_page,
                    'type': 'public'
                }
                
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                page_repos = response.json()
                if not page_repos:
                    break
                    
                repos.extend(page_repos)
                logger.info(f"获取第{page}页，找到{len(page_repos)}个仓库")
                
                page += 1
                time.sleep(0.1)  # 避免API限制
                
            except requests.exceptions.RequestException as e:
                logger.error(f"获取仓库列表失败: {e}")
                break
                
        logger.info(f"总共获取到{len(repos)}个仓库")
        return repos
    
    def get_repo_readme(self, repo_name: str) -> Optional[str]:
        """
        获取指定仓库的README文件内容
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            README文件内容，如果不存在返回None
        """
        readme_files = ['README.md', 'readme.md', 'README.txt', 'readme.txt', 'README']
        
        for readme_file in readme_files:
            try:
                url = f"{self.base_url}/repos/{self.org_name}/{repo_name}/contents/{readme_file}"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    content_data = response.json()
                    
                    # 解码base64内容
                    if content_data.get('encoding') == 'base64':
                        readme_content = base64.b64decode(content_data['content']).decode('utf-8')
                        logger.info(f"成功获取{repo_name}的{readme_file}")
                        return readme_content
                        
            except Exception as e:
                logger.warning(f"获取{repo_name}的{readme_file}失败: {e}")
                continue
                
        logger.warning(f"仓库{repo_name}未找到README文件")
        return None
    
    def save_readme_to_file(self, repo_name: str, content: str) -> str:
        """
        将README内容保存到文件
        
        Args:
            repo_name: 仓库名称
            content: README内容
            
        Returns:
            保存的文件路径
        """
        # 创建仓库目录
        repo_dir = os.path.join(self.readme_dir, repo_name)
        os.makedirs(repo_dir, exist_ok=True)
        
        # 保存为README.md
        filepath = os.path.join(repo_dir, "README.md")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"README保存成功: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存README失败: {e}")
            raise
    
    def collect_all_readmes(self) -> Dict[str, str]:
        """
        收集所有仓库的README文件
        
        Returns:
            仓库名称到文件路径的映射
        """
        logger.info("开始收集所有README文件")
        
        # 获取仓库列表
        repos = self.get_organization_repos()
        if not repos:
            logger.error("未获取到任何仓库")
            return {}
        
        success_count = 0
        failed_count = 0
        file_paths = {}
        
        for repo in repos:
            repo_name = repo['name']
            logger.info(f"处理仓库: {repo_name}")
            
            try:
                # 获取README内容
                readme_content = self.get_repo_readme(repo_name)
                
                if readme_content:
                    # 添加仓库元信息到README前面
                    repo_info = f"""# {repo_name}

**仓库描述**: {repo.get('description', '无描述')}
**仓库地址**: {repo.get('html_url', '')}
**创建时间**: {repo.get('created_at', '')}
**更新时间**: {repo.get('updated_at', '')}
**主要语言**: {repo.get('language', '未知')}
**Star数**: {repo.get('stargazers_count', 0)}

---

{readme_content}
"""
                    
                    # 保存到文件
                    filepath = self.save_readme_to_file(repo_name, repo_info)
                    file_paths[repo_name] = filepath
                    success_count += 1
                else:
                    failed_count += 1
                    
                # 避免API限制
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"处理仓库{repo_name}时出错: {e}")
                failed_count += 1
                continue
        
        logger.info(f"README收集完成: 成功{success_count}个，失败{failed_count}个")
        
        # 保存收集结果统计
        self.save_collection_summary(repos, file_paths)
        
        return file_paths
    
    def save_collection_summary(self, repos: List[Dict], file_paths: Dict[str, str]):
        """
        保存收集结果统计
        
        Args:
            repos: 仓库列表
            file_paths: 成功收集的文件路径
        """
        summary = {
            'collection_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_repos': len(repos),
            'successful_collections': len(file_paths),
            'failed_collections': len(repos) - len(file_paths),
            'collected_repos': list(file_paths.keys()),
            'file_paths': file_paths
        }
        
        summary_path = os.path.join(self.readme_dir, 'collection_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"收集统计保存到: {summary_path}")


def main():
    """主函数"""
    try:
        # 创建收集器实例
        collector = DatawhaleRepoCollector()
        
        # 开始收集README文件
        result = collector.collect_all_readmes()
        
        print(f"README收集完成！")
        print(f"成功收集: {len(result)}个仓库")
        print(f"文件保存位置: {collector.readme_dir}")
        
        return result
        
    except Exception as e:
        logger.error(f"收集过程中出现错误: {e}")
        print(f"错误: {e}")
        return {}


if __name__ == "__main__":
    main()
