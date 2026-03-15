#!/usr/bin/env python3
"""
主更新脚本 - 自动更新 GitHub 中文项目排行榜
"""

import os
import sys
from datetime import datetime

# 添加 utils 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

# 直接导入模块
import importlib.util

def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

scraper = import_module_from_file('scraper', os.path.join(os.path.dirname(__file__), '..', 'utils', 'scraper.py'))
analyzer = import_module_from_file('analyzer', os.path.join(os.path.dirname(__file__), '..', 'utils', 'analyzer.py'))
classifier = import_module_from_file('classifier', os.path.join(os.path.dirname(__file__), '..', 'utils', 'classifier.py'))
exporter = import_module_from_file('exporter', os.path.join(os.path.dirname(__file__), '..', 'utils', 'exporter.py'))

# 获取函数
calculate_overall_score = analyzer.calculate_overall_score
scrape_all = scraper.scrape_all
filter_chinese_projects = scraper.filter_chinese_projects
classify_repos = classifier.classify_repos
generate_markdown_report = classifier.generate_markdown_report
save_to_json = exporter.save_to_json
save_to_csv = exporter.save_to_csv
save_stats = exporter.save_stats


def main():
    print("=" * 60)
    print("GitHub 中文项目排行榜 - 自动更新")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 抓取项目
    print("步骤 1/5: 抓取 GitHub 项目...")
    github_api = scraper.get_github_api()

    repos = scrape_all(github_api)
    print(f"抓取完成，共 {len(repos)} 个项目\n")

    # 2. 过滤中文项目
    print("步骤 2/5: 过滤中文项目...")
    chinese_repos = filter_chinese_projects(repos)
    print(f"过滤完成，共 {len(chinese_repos)} 个中文项目\n")

    # 3. 计算评分
    print("步骤 3/5: 计算项目评分...")
    scored_repos = []
    for i, repo in enumerate(chinese_repos, 1):
        print(f"[{i}/{len(chinese_repos)}] {repo['owner']}/{repo['repo']}", end=" ")

        # 计算评分
        score_result = calculate_overall_score(repo, github_api)
        repo.update(score_result)
        scored_repos.append(repo)

        print(f"✓ ({score_result['score']:.1f})")

    print(f"评分完成，共 {len(scored_repos)} 个项目\n")

    # 4. 分类项目
    print("步骤 4/5: 分类项目...")
    classified_repos = classify_repos(scored_repos)
    print(f"分类完成，共 {len(classified_repos)} 个分类\n")

    for category, repos in sorted(classified_repos.items()):
        print(f"- {category}: {len(repos)} 个项目")

    print()

    # 5. 生成报告
    print("步骤 5/5: 生成报告...")
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'categories')
    os.makedirs(output_dir, exist_ok=True)

    # 生成 Markdown 报告
    generate_markdown_report(classified_repos, os.path.join(output_dir, "README.md"))

    # 保存原始数据
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    save_to_json(scored_repos, os.path.join(data_dir, "projects.json"))
    save_to_csv(scored_repos, os.path.join(data_dir, "projects.csv"))

    # 生成统计信息
    stats = {
        "total_projects": len(scored_repos),
        "total_stars": sum(repo.get('stars', 0) for repo in scored_repos),
        "average_score": sum(repo.get('score', 0) for repo in scored_repos) / len(scored_repos) if scored_repos else 0,
        "by_rating": {},
        "by_category": {}
    }

    for repo in scored_repos:
        rating = repo.get('rating', 'unknown')
        stats['by_rating'][rating] = stats['by_rating'].get(rating, 0) + 1

        category = repo.get('category', 'unknown')
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

    save_stats(stats, os.path.join(data_dir, "stats.md"))

    print()

    # 打印总结
    print("=" * 60)
    print("更新完成！")
    print("=" * 60)
    print(f"总项目数: {stats['total_projects']}")
    print(f"总 Star 数: {stats['total_stars']:,}")
    print(f"平均评分: {stats['average_score']:.1f}")
    print()
    print("生成的文件:")
    print(f"  - {os.path.join(data_dir, 'projects.json')}")
    print(f"  - {os.path.join(data_dir, 'projects.csv')}")
    print(f"  - {os.path.join(data_dir, 'stats.md')}")
    print(f"  - {os.path.join(output_dir, 'README.md')}")
    print()
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
