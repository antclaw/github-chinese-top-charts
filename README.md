# GitHub 中文优质项目排行榜

> 收录所有领域的高质量中文 GitHub 项目，每周自动更新

## 📊 收录标准

我们不只是看 Star 数，而是综合评估以下三个维度：

### 1. 文档质量 ✅
- README 是否清晰详细
- 有中文文档
- 代码注释完整
- 有使用示例

### 2. 社区活跃度 📈
- 最近 30 天有更新
- Issue 反应及时
- PR 流程规范
- 有中文 Issue/PR

### 3. 实用性 🎯
- 解决实际问题
- 代码质量高
- 可维护性强
- 有持续维护意愿

## 🗂️ 分类

### 技术开发
- AI/机器学习
- 后端开发
- 前端开发
- 移动开发
- DevOps
- 测试/QA
- 其他技术

### 工具类
- CLI 工具
- 开发工具
- 数据处理
- 图形界面
- 其他工具

### 学习资源
- 编程教程
- 在线课程
- 书籍推荐
- 学习路径

### 游戏
- 网页游戏
- 桌面游戏
- 移动游戏
- 其他游戏

### 其他领域
- 设计
- 产品
- 翻译
- 其他

## 🔄 更新频率

每周一更新一次，自动抓取并更新排行榜。

## 📁 项目结构

```
github-chinese-top-charts/
├── README.md
├── README_EN.md
├── categories/          # 各分类的 Markdown 文件
│   ├── ai.md
│   ├── backend.md
│   ├── frontend.md
│   └── ...
├── data/               # 原始数据
│   ├── projects.json
│   └── scores.json
├── scripts/            # 自动化脚本
│   ├── scrape.py
│   ├── update.py
│   └── validate.py
└── utils/              # 工具函数
    ├── scraper.py
    ├── analyzer.py
    └── exporter.py
```

## 🚀 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行更新

```bash
python scripts/update.py
```

### 查看排行榜

直接打开对应的 Markdown 文件即可查看。

## 🤝 贡献

如果你发现优秀的中文项目，欢迎提交 PR！

## 📝 License

MIT

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐
