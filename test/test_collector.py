#!/usr/bin/env python3
"""
测试脚本：验证GitHub API调用功能
注意：需要在.env文件中配置有效的GitHub TOKEN
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.test_getall_repo import DatawhaleRepoCollector

def test_repo_collector():
    """测试仓库收集器"""
    print("开始测试GitHub仓库收集器...")
    
    try:
        # 检查环境变量
        if not os.getenv('TOKEN'):
            print("⚠️  警告: 未找到GitHub TOKEN环境变量")
            print("请在.env文件中配置TOKEN=your_github_token")
            print("或者设置环境变量: export TOKEN=your_github_token")
            return False
        
        # 创建收集器实例
        collector = DatawhaleRepoCollector()
        print("✅ 收集器初始化成功")
        
        # 测试获取仓库列表（只获取前几个）
        print("📋 测试获取仓库列表...")
        repos = collector.get_organization_repos()
        
        if repos:
            print(f"✅ 成功获取到 {len(repos)} 个仓库")
            print("前5个仓库:")
            for i, repo in enumerate(repos[:5]):
                print(f"  {i+1}. {repo['name']} - {repo.get('description', '无描述')}")
        else:
            print("❌ 未获取到任何仓库")
            return False
            
        # 测试获取单个README（测试第一个仓库）
        if repos:
            test_repo = repos[0]['name']
            print(f"\n📖 测试获取README: {test_repo}")
            readme_content = collector.get_repo_readme(test_repo)
            
            if readme_content:
                print(f"✅ 成功获取README，长度: {len(readme_content)} 字符")
                print("前200个字符预览:")
                print(readme_content[:200] + "..." if len(readme_content) > 200 else readme_content)
            else:
                print(f"⚠️  仓库 {test_repo} 没有找到README文件")
        
        print("\n🎉 测试完成！收集器功能正常")
        return True
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_repo_collector()
    sys.exit(0 if success else 1)