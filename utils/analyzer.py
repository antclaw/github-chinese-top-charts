#!/usr/bin/env python3
"""
评分系统：评估中文 GitHub 项目的质量
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any

# 评分标准

DOCUMENTATION_SCORES = {
    "excellent": 30,  # 文档非常详细，有示例，有教程
    "good": 20,      # 文档清晰，有基本说明
    "average": 10,   # 有基本文档
    "poor": 5,       # 文档缺失或非常简略
    "none": 0        # 无文档
}

COMMUNITY_SCORES = {
    "very_active": 30,  # 每周都有更新，Issue 回复快
    "active": 20,       # 每月有更新，Issue 回复及时
    "moderate": 10,     # 偶尔更新，Issue 回复一般
    "inactive": 5,      # 很少更新，Issue 回复慢
    "dead": 0           # 长期无更新
}

PRACTICALITY_SCORES = {
    "high": 40,         # 解决实际问题，代码质量高
    "medium": 25,       # 有一定实用性
    "low": 10,          # 实用性一般
    "none": 0           # 无实用价值
}


def calculate_documentation_score(readme: str) -> tuple:
    """
    计算文档质量分数

    Args:
        readme: README 内容

    Returns:
        (score, details)
    """
    score = 0
    details = []

    # 检查是否有中文文档
    if re.search(r'[\u4e00-\u9fff]', readme):
        score += 5
        details.append("有中文文档")

    # 检查 README 长度
    if len(readme) > 500:
        score += 5
        details.append("README 较长")

    # 检查是否有使用示例
    if re.search(r'```[\s\S]*?```', readme):
        score += 5
        details.append("有代码示例")

    # 检查是否有安装指南
    if re.search(r'install|安装|setup|配置', readme, re.IGNORECASE):
        score += 5
        details.append("有安装/配置指南")

    # 检查是否有功能介绍
    if re.search(r'功能|features|特性|介绍', readme, re.IGNORECASE):
        score += 5
        details.append("有功能介绍")

    # 检查是否有项目结构说明
    if re.search(r'目录结构|结构|架构', readme, re.IGNORECASE):
        score += 5
        details.append("有项目结构说明")

    # 评级
    if score >= 25:
        rating = "excellent"
    elif score >= 15:
        rating = "good"
    elif score >= 8:
        rating = "average"
    else:
        rating = "poor"

    return DOCUMENTATION_SCORES[rating], details


def calculate_community_score(owner: str, repo: str, github_api) -> tuple:
    """
    计算社区活跃度分数

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        github_api: GitHub API 客户端

    Returns:
        (score, details)
    """
    score = 0
    details = []

    try:
        # 获取最近 30 天的提交记录
        commits = github_api.get_repo_commits(owner, repo, since=datetime.now() - timedelta(days=30))
        commit_count = len(commits)

        if commit_count >= 10:
            score += 10
            details.append(f"最近30天提交{commit_count}次")
        elif commit_count >= 5:
            score += 7
            details.append(f"最近30天提交{commit_count}次")
        elif commit_count >= 2:
            score += 5
            details.append(f"最近30天提交{commit_count}次")
        elif commit_count >= 1:
            score += 3
            details.append(f"最近30天提交{commit_count}次")
        else:
            score += 1
            details.append("提交较少")

        # 获取 Issues 统计
        issues = github_api.get_repo_issues(owner, repo, state='open')
        open_issues = len(issues)

        if open_issues <= 5:
            score += 10
            details.append(f"Open Issues: {open_issues}个")
        elif open_issues <= 10:
            score += 7
            details.append(f"Open Issues: {open_issues}个")
        else:
            score += 5
            details.append(f"Open Issues: {open_issues}个")

        # 检查是否有中文 Issue
        has_chinese_issue = any(
            re.search(r'[\u4e00-\u9fff]', issue['title'] + issue['body'])
            for issue in issues[:10]
        )

        if has_chinese_issue:
            score += 5
            details.append("有中文 Issue")

    except Exception as e:
        score = 5
        details.append(f"无法获取社区数据: {str(e)}")

    # 评级
    if score >= 25:
        rating = "very_active"
    elif score >= 15:
        rating = "active"
    elif score >= 8:
        rating = "moderate"
    elif score >= 3:
        rating = "inactive"
    else:
        rating = "dead"

    return COMMUNITY_SCORES[rating], details


def calculate_practicality_score(readme: str) -> tuple:
    """
    计算实用性分数

    Args:
        readme: README 内容

    Returns:
        (score, details)
    """
    score = 0
    details = []

    # 检查是否有 README
    if len(readme) < 50:
        return 0, ["无 README"]

    # 检查是否有明确的项目目标
    if re.search(r'目的|目标|作用|用途', readme):
        score += 10
        details.append("有明确的项目目标")

    # 检查是否有 License
    if re.search(r'license|MIT|Apache|GPL', readme, re.IGNORECASE):
        score += 10
        details.append("有 License")

    # 检查是否有贡献指南
    if re.search(r'contribute|贡献|PR', readme, re.IGNORECASE):
        score += 10
        details.append("有贡献指南")

    # 检查是否有测试文件
    if re.search(r'test|测试', readme, re.IGNORECASE):
        score += 5
        details.append("有测试")

    # 检查是否有 CI/CD 配置
    if re.search(r'github.*workflow|CI|CD', readme, re.IGNORECASE):
        score += 5
        details.append("有 CI/CD 配置")

    # 检查 Star 数（作为参考）
    # 这里假设已经有 Star 数，实际使用时传入

    # 评级
    if score >= 30:
        rating = "high"
    elif score >= 15:
        rating = "medium"
    elif score >= 5:
        rating = "low"
    else:
        rating = "none"

    return PRACTICALITY_SCORES[rating], details


def calculate_overall_score(repo_data: Dict[str, Any], github_api=None) -> Dict[str, Any]:
    """
    计算综合评分

    Args:
        repo_data: 仓库数据
        github_api: GitHub API 客户端（可选）

    Returns:
        评分结果
    """
    result = {
        "owner": repo_data.get("owner", ""),
        "repo": repo_data.get("repo", ""),
        "stars": repo_data.get("stars", 0),
        "url": repo_data.get("url", ""),
        "score": 0,
        "details": {},
        "rating": ""
    }

    # 获取 README
    readme = repo_data.get("readme", "")

    # 1. 计算文档质量
    doc_score, doc_details = calculate_documentation_score(readme)
    result["details"]["documentation"] = {
        "score": doc_score,
        "details": doc_details,
        "rating": list(DOCUMENTATION_SCORES.keys())[list(DOCUMENTATION_SCORES.values()).index(doc_score)]
    }

    # 2. 计算社区活跃度
    if github_api:
        comm_score, comm_details = calculate_community_score(
            result["owner"], result["repo"], github_api
        )
    else:
        comm_score = 10
        comm_details = ["无法获取社区数据"]
        result["details"]["community"] = {
            "score": comm_score,
            "details": comm_details,
            "rating": "moderate"
        }

    # 3. 计算实用性
    prac_score, prac_details = calculate_practicality_score(readme)
    result["details"]["practicality"] = {
        "score": prac_score,
        "details": prac_details,
        "rating": list(PRACTICALITY_SCORES.keys())[list(PRACTICALITY_SCORES.values()).index(prac_score)]
    }

    # 计算总分（权重：文档 30%，社区 30%，实用性 40%）
    result["score"] = doc_score * 0.3 + comm_score * 0.3 + prac_score * 0.4

    # 评级
    if result["score"] >= 80:
        result["rating"] = "excellent"
    elif result["score"] >= 60:
        result["rating"] = "good"
    elif result["score"] >= 40:
        result["rating"] = "average"
    else:
        result["rating"] = "poor"

    return result


if __name__ == "__main__":
    # 测试
    test_repo = {
        "owner": "vuejs",
        "repo": "vue",
        "stars": 200000,
        "url": "https://github.com/vuejs/vue",
        "readme": """
# Vue.js

Vue.js is a progressive JavaScript framework for building user interfaces.

## Features

- Declarative rendering
- Component-based architecture
- Reactive data binding
- Virtual DOM

## Installation

```bash
npm install vue
```

## Quick Start

```javascript
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

## Documentation

Full documentation at [vuejs.org](https://vuejs.org)

## License

MIT
"""
    }

    score = calculate_overall_score(test_repo)
    print(f"项目: {score['owner']}/{score['repo']}")
    print(f"总分: {score['score']:.1f}")
    print(f"评级: {score['rating']}")
    print(f"文档质量: {score['details']['documentation']['score']} - {score['details']['documentation']['details']}")
    print(f"社区活跃度: {score['details']['community']['score']} - {score['details']['community']['details']}")
    print(f"实用性: {score['details']['practicality']['score']} - {score['details']['practicality']['details']}")
