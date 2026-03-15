#!/usr/bin/env python3
"""
项目分类器
"""

import re
from typing import List, Dict, Any
from datetime import datetime


# 分类规则
CATEGORY_RULES = {
    "ai": {
        "keywords": ["ai", "artificial intelligence", "machine learning", "deep learning", "nlp", "computer vision", "llm", "gpt", "transformer", "神经网络"],
        "aliases": ["人工智能", "机器学习", "深度学习", "自然语言处理", "计算机视觉", "大模型"]
    },
    "backend": {
        "keywords": ["backend", "api", "server", "database", "sql", "nosql", "rest", "graphql", "microservices", "spring", "django", "flask", "express", "koa", "gin"],
        "aliases": ["后端", "API", "服务器", "数据库", "REST", "GraphQL", "微服务", "Spring", "Django", "Flask"]
    },
    "frontend": {
        "keywords": ["frontend", "vue", "react", "angular", "reactive", "component", "ui", "ux", "css", "javascript", "typescript", "svelte", "preact"],
        "aliases": ["前端", "Vue", "React", "Angular", "UI", "CSS", "JavaScript", "TypeScript"]
    },
    "mobile": {
        "keywords": ["mobile", "ios", "android", "flutter", "react native", "capacitor", "ionic", "app", "mobile app"],
        "aliases": ["移动", "iOS", "Android", "Flutter", "React Native", "App"]
    },
    "devops": {
        "keywords": ["devops", "docker", "kubernetes", "ci/cd", "pipeline", "jenkins", "github actions", "travis", "circleci", "terraform", "ansible", "chef", "puppet"],
        "aliases": ["DevOps", "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitHub Actions"]
    },
    "testing": {
        "keywords": ["test", "testing", "qa", "unittest", "pytest", "jest", "cypress", "selenium", "mock", "mocking"],
        "aliases": ["测试", "QA", "单元测试", "Pytest", "Jest", "Cypress"]
    },
    "cli": {
        "keywords": ["cli", "command line", "terminal", "shell", "bash", "zsh", "powershell", "console"],
        "aliases": ["CLI", "命令行", "终端", "Shell", "Bash", "Zsh"]
    },
    "tool": {
        "keywords": ["tool", "utility", "helper", "script", "automation", "scripting", "converter", "formatter", "editor", "IDE"],
        "aliases": ["工具", "实用", "脚本", "自动化", "转换器", "格式化"]
    },
    "data": {
        "keywords": ["data", "data processing", "data analysis", "pandas", "numpy", "spark", "etl", "data science", "big data"],
        "aliases": ["数据", "数据处理", "数据分析", "Pandas", "NumPy", "Spark"]
    },
    "game": {
        "keywords": ["game", "game engine", "unity", "unreal", "godot", "cocos", "phaser", "webgl"],
        "aliases": ["游戏", "游戏引擎", "Unity", "Unreal", "Godot", "Cocos"]
    },
    "learning": {
        "keywords": ["tutorial", "course", "learning", "education", "book", "document", "guide", "docs"],
        "aliases": ["教程", "课程", "学习", "教育", "书籍", "文档", "指南"]
    },
    "design": {
        "keywords": ["design", "ui", "ux", "figma", "sketch", "design system", "prototype"],
        "aliases": ["设计", "UI", "UX", "Figma", "Sketch", "设计系统"]
    },
    "product": {
        "keywords": ["product", "productivity", "workflow", "planner", "manager", "task", "todo"],
        "aliases": ["产品", "生产力", "工作流", "计划", "管理", "任务"]
    }
}


def classify_repo(repo: Dict[str, Any]) -> str:
    """
    分类仓库

    Args:
        repo: 仓库数据

    Returns:
        分类名称
    """
    # 检查 topics
    topics = repo.get('topics', [])
    for topic in topics:
        for category, rules in CATEGORY_RULES.items():
            if topic.lower() in rules['keywords'] or topic.lower() in rules['aliases']:
                return category

    # 检查 README
    readme = repo.get('readme', '').lower()
    description = repo.get('description', '').lower()

    # 合并关键词
    all_text = readme + " " + description

    # 检查每个分类
    for category, rules in CATEGORY_RULES.items():
        for keyword in rules['keywords']:
            if keyword in all_text:
                return category

    # 默认分类
    return "other"


def classify_repos(repos: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    分类多个仓库

    Args:
        repos: 仓库列表

    Returns:
        分类字典 {category: [repos]}
    """
    classified = {}

    for repo in repos:
        category = classify_repo(repo)
        if category not in classified:
            classified[category] = []
        classified[category].append(repo)

    return classified


def sort_repos_by_score(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    按评分排序

    Args:
        repos: 仓库列表

    Returns:
        排序后的仓库列表
    """
    return sorted(repos, key=lambda x: x.get('score', 0), reverse=True)


def generate_markdown_report(classified_repos: Dict[str, List[Dict[str, Any]]], output_file: str = "categories/README.md"):
    """
    生成 Markdown 报告

    Args:
        classified_repos: 分类后的仓库
        output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# GitHub 中文优质项目排行榜\n\n")
        f.write(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for category in sorted(classified_repos.keys()):
            repos = classified_repos[category]
            if not repos:
                continue

            # 按评分排序
            sorted_repos = sort_repos_by_score(repos)

            f.write(f"## {category.capitalize()}\n\n")
            f.write(f"共 {len(sorted_repos)} 个项目\n\n")

            for i, repo in enumerate(sorted_repos[:50], 1):  # 每个分类最多 50 个
                score = repo.get('score', 0)
                stars = repo.get('stars', 0)
                rating = repo.get('rating', 'unknown')

                f.write(f"### {i}. [{repo['owner']}/{repo['repo']}]({repo['url']})\n\n")
                f.write(f"**评分**: {score:.1f} ({rating})\n\n")
                f.write(f"**Stars**: {stars:,}\n\n")
                f.write(f"{repo.get('description', '')}\n\n")

                if repo.get('details', {}).get('documentation'):
                    doc = repo['details']['documentation']
                    f.write(f"- 文档质量: {doc['score']}/30 - {', '.join(doc['details'][:3])}\n")

                if repo.get('details', {}).get('community'):
                    comm = repo['details']['community']
                    f.write(f"- 社区活跃度: {comm['score']}/30 - {', '.join(comm['details'][:3])}\n")

                if repo.get('details', {}).get('practicality'):
                    prac = repo['details']['practicality']
                    f.write(f"- 实用性: {prac['score']}/40 - {', '.join(prac['details'][:3])}\n")

                f.write("---\n\n")

    print(f"Markdown 报告已生成: {output_file}")


if __name__ == "__main__":
    # 测试
    test_repos = [
        {
            "owner": "vuejs",
            "repo": "vue",
            "url": "https://github.com/vuejs/vue",
            "description": "Vue.js - 渐进式 JavaScript 框架",
            "topics": ["javascript", "framework", "frontend", "vue", "vue3"],
            "readme": "Vue.js is a progressive JavaScript framework for building user interfaces.",
            "score": 85,
            "rating": "excellent",
            "stars": 200000,
            "details": {
                "documentation": {"score": 25, "details": ["有中文文档", "有代码示例", "有安装指南"]},
                "community": {"score": 25, "details": ["最近30天提交10次", "Open Issues: 3个", "有中文 Issue"]},
                "practicality": {"score": 35, "details": ["有明确的项目目标", "有 License", "有贡献指南"]}
            }
        },
        {
            "owner": "facebook",
            "repo": "react",
            "url": "https://github.com/facebook/react",
            "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
            "topics": ["javascript", "library", "frontend", "react"],
            "readme": "React is a JavaScript library for building user interfaces.",
            "score": 80,
            "rating": "good",
            "stars": 210000,
            "details": {
                "documentation": {"score": 22, "details": ["有中文文档", "有代码示例"]},
                "community": {"score": 23, "details": ["最近30天提交8次", "Open Issues: 5个"]},
                "practicality": {"score": 35, "details": ["有明确的项目目标", "有 License", "有贡献指南"]}
            }
        },
        {
            "owner": "openai",
            "repo": "gpt-3",
            "url": "https://github.com/openai/gpt-3",
            "description": "OpenAI's GPT-3 model",
            "topics": ["ai", "nlp", "transformer"],
            "readme": "GPT-3: Language Models are Few-Shot Learners",
            "score": 75,
            "rating": "good",
            "stars": 150000,
            "details": {
                "documentation": {"score": 20, "details": ["有中文文档"]},
                "community": {"score": 20, "details": ["最近30天提交5次"]},
                "practicality": {"score": 35, "details": ["有明确的项目目标", "有 License"]}
            }
        }
    ]

    classified = classify_repos(test_repos)
    generate_markdown_report(classified)
