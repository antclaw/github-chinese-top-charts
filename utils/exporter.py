#!/usr/bin/env python3
"""
数据导出器
"""

import json
from typing import List, Dict, Any
from datetime import datetime


def save_to_json(data: List[Dict[str, Any]], output_file: str):
    """
    保存为 JSON 文件

    Args:
        data: 数据列表
        output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON 数据已保存: {output_file}")


def save_to_csv(data: List[Dict[str, Any]], output_file: str):
    """
    保存为 CSV 文件

    Args:
        data: 数据列表
        output_file: 输出文件路径
    """
    import csv

    if not data:
        print("无数据可导出")
        return

    # 获取所有字段
    fields = set()
    for item in data:
        fields.update(item.keys())

    fields = list(fields)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

    print(f"CSV 数据已保存: {output_file}")


def generate_stats(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成统计数据

    Args:
        data: 数据列表

    Returns:
        统计信息
    """
    stats = {
        "total_projects": len(data),
        "total_stars": sum(repo.get('stars', 0) for repo in data),
        "average_score": sum(repo.get('score', 0) for repo in data) / len(data) if data else 0,
        "by_rating": {},
        "by_category": {}
    }

    # 按评级统计
    for repo in data:
        rating = repo.get('rating', 'unknown')
        stats['by_rating'][rating] = stats['by_rating'].get(rating, 0) + 1

    # 按分类统计
    classified = {}
    for repo in data:
        category = repo.get('category', 'unknown')
        classified[category] = classified.get(category, 0) + 1

    stats['by_category'] = classified

    return stats


def save_stats(stats: Dict[str, Any], output_file: str):
    """
    保存统计数据

    Args:
        stats: 统计信息
        output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 统计信息\n\n")
        f.write(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"总项目数: {stats['total_projects']}\n\n")
        f.write(f"总 Star 数: {stats['total_stars']:,}\n\n")
        f.write(f"平均评分: {stats['average_score']:.1f}\n\n")

        f.write("## 按评级统计\n\n")
        for rating, count in sorted(stats['by_rating'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {rating}: {count}\n")

        f.write("\n## 按分类统计\n\n")
        for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {category}: {count}\n")

    print(f"统计信息已保存: {output_file}")


if __name__ == "__main__":
    # 测试
    test_data = [
        {
            "owner": "vuejs",
            "repo": "vue",
            "url": "https://github.com/vuejs/vue",
            "description": "Vue.js - 渐进式 JavaScript 框架",
            "stars": 200000,
            "score": 85,
            "rating": "excellent",
            "category": "frontend"
        },
        {
            "owner": "tensorflow",
            "repo": "tensorflow",
            "url": "https://github.com/tensorflow/tensorflow",
            "description": "An Open Source Machine Learning Framework",
            "stars": 180000,
            "score": 82,
            "rating": "good",
            "category": "ai"
        },
        {
            "owner": "facebook",
            "repo": "react",
            "url": "https://github.com/facebook/react",
            "description": "A declarative, efficient, and flexible JavaScript library",
            "stars": 210000,
            "score": 80,
            "rating": "good",
            "category": "frontend"
        }
    ]

    stats = generate_stats(test_data)
    save_stats(stats, "stats.md")
