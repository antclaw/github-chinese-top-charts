#!/usr/bin/env python3
"""
GitHub 中文项目抓取器
"""

import requests
import re
from typing import List, Dict, Any
from datetime import datetime
import sys
import os
import importlib.util
from datetime import datetime

# 确保 utils 目录在路径中
utils_dir = os.path.dirname(__file__)
if utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)

# 动态导入 analyzer
analyzer_path = os.path.join(utils_dir, "analyzer.py")
spec = importlib.util.spec_from_file_location("analyzer", analyzer_path)
analyzer = importlib.util.module_from_spec(spec)
sys.modules['analyzer'] = analyzer
spec.loader.exec_module(analyzer)

calculate_overall_score = analyzer.calculate_overall_score

# 读取 GitHub API Token
GITHUB_TOKEN = ""
token_file = os.path.join(os.path.dirname(__file__), '..', '..', '.secrets', 'github-tenant-token.txt')
if os.path.exists(token_file):
    with open(token_file, 'r') as f:
        token = f.read().strip()
        if token and token != 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            GITHUB_TOKEN = token

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "GitHub-Chinese-Top-Charts/1.0"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"


def get_github_api():
    """获取 GitHub API 客户端"""
    return requests.Session()


def search_chinese_repos(query: str, github_api) -> List[Dict[str, Any]]:
    """
    搜索中文仓库

    Args:
        query: 搜索查询
        github_api: GitHub API 客户端

    Returns:
        仓库列表
    """
    repos = []

    try:
        # 搜索中文项目
        url = f"https://api.github.com/search/repositories?q={query}+language:python&sort=stars&order=desc"
        response = github_api.get(url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", [])[:50]:  # 限制前 50 个
                repos.append({
                    "owner": item["owner"]["login"],
                    "repo": item["name"],
                    "stars": item["stargazers_count"],
                    "url": item["html_url"],
                    "description": item["description"] or "",
                    "language": item["language"],
                    "topics": item.get("topics", []),
                    "updated_at": item["updated_at"],
                    "created_at": item["created_at"],
                    "homepage": item.get("homepage", ""),
                    "license": item.get("license", {}).get("name", "")
                })
        else:
            print(f"搜索失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"搜索出错: {str(e)}")

    return repos


def fetch_readme(owner: str, repo: str, github_api) -> str:
    """
    获取仓库的 README

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        github_api: GitHub API 客户端

    Returns:
        README 内容
    """
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        response = github_api.get(url, headers=HEADERS)

        if response.status_code == 200:
            import base64
            data = response.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
        else:
            return ""
    except Exception as e:
        print(f"获取 README 失败: {owner}/{repo} - {str(e)}")
        return ""


def search_by_language(github_api) -> List[Dict[str, Any]]:
    """
    按语言搜索中文项目

    Args:
        github_api: GitHub API 客户端

    Returns:
        仓库列表
    """
    repos = []

    # 常见编程语言
    languages = ["python", "javascript", "typescript", "java", "go", "rust", "php", "ruby", "swift", "kotlin"]

    for lang in languages:
        print(f"搜索 {lang} 中文项目...")
        lang_repos = search_chinese_repos(f"{lang}+readme", github_api)
        repos.extend(lang_repos)

    return repos


def search_by_topic(github_api) -> List[Dict[str, Any]]:
    """
    按主题搜索中文项目

    Args:
        github_api: GitHub API 客户端

    Returns:
        仓库列表
    """
    repos = []

    # 常见主题
    topics = [
        "ai", "machine-learning", "deep-learning", "computer-vision",
        "web", "frontend", "backend", "devops", "docker", "kubernetes",
        "data-science", "数据分析", "automation", "script",
        "tool", "cli", "gui", "game"
    ]

    for topic in topics:
        print(f"搜索主题 {topic} 中文项目...")
        topic_repos = search_chinese_repos(f"{topic}+readme", github_api)
        repos.extend(topic_repos)

    return repos


def scrape_all(github_api) -> List[Dict[str, Any]]:
    """
    抓取所有中文项目

    Args:
        github_api: GitHub API 客户端

    Returns:
        仓库列表
    """
    print("=" * 50)
    print("开始抓取 GitHub 中文项目...")
    print("=" * 50)

    # 按语言搜索
    repos_by_lang = search_by_language(github_api)
    print(f"\n按语言搜索到 {len(repos_by_lang)} 个项目")

    # 按主题搜索
    repos_by_topic = search_by_topic(github_api)
    print(f"按主题搜索到 {len(repos_by_topic)} 个项目")

    # 合并并去重
    all_repos = repos_by_lang + repos_by_topic
    unique_repos = []
    seen = set()

    for repo in all_repos:
        key = f"{repo['owner']}/{repo['repo']}"
        if key not in seen:
            seen.add(key)
            unique_repos.append(repo)

    print(f"去重后剩余 {len(unique_repos)} 个项目")

    # 获取 README
    print("\n获取 README...")
    for i, repo in enumerate(unique_repos, 1):
        print(f"[{i}/{len(unique_repos)}] {repo['owner']}/{repo['repo']}", end=" ")
        readme = fetch_readme(repo['owner'], repo['repo'], github_api)
        repo['readme'] = readme
        print("✓")

    return unique_repos


def filter_chinese_projects(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    过滤出中文项目

    Args:
        repos: 仓库列表

    Returns:
        中文项目列表
    """
    chinese_repos = []

    for repo in repos:
        readme = repo.get('readme', '')
        description = repo.get('description', '')

        # 检查 README 和描述中是否有中文
        has_chinese = re.search(r'[\u4e00-\u9fff]', readme) or re.search(r'[\u4e00-\u9fff]', description)

        if has_chinese:
            repo['has_chinese'] = True
            chinese_repos.append(repo)

    return chinese_repos


if __name__ == "__main__":
    github_api = get_github_api()
    repos = scrape_all(github_api)
    print(f"\n总共抓取 {len(repos)} 个项目")

    # 过滤中文项目
    chinese_repos = filter_chinese_projects(repos)
    print(f"其中 {len(chinese_repos)} 个是中文项目")
