---
name: openspec-compound
description: "为 OpenSpec 工作流添加知识沉淀与复用能力，将变更中的可复用方案提炼到 openspec/solutions/ 知识库。TRIGGER when: 用户调用 /opsx:compound、/opsx:compound-search 或 /opsx:compound-refresh；完成 OpenSpec 变更后提到「沉淀知识」「记录方案」「整理经验」；规划新变更时想查「历史经验」「类似方案」「solutions 目录」。SKIP: 标准 OpenSpec propose/apply/archive 流程且未涉及知识沉淀的场景。"
---

# OpenSpec Compound Skill

将 OpenSpec 变更中的可复用技术方案提炼到 `openspec/solutions/` 知识库，供未来规划时自动参考。

## 命令

加载 `commands/` 目录中对应文件执行：

| 命令 | 功能 | 使用时机 |
|------|------|---------|
| `/opsx:compound [变更名]` | 从已完成变更提取可复用方案并保存 | 变更 apply 完成后 |
| `/opsx:compound-search <关键词>` | 搜索 solutions 知识库 | 规划前或随时查阅 |
| `/opsx:compound-refresh` | 重建索引、修复链接、清理过时内容 | 定期维护 |

## 知识库结构

```
openspec/solutions/
├── _index.json        # 自动维护的检索索引
└── *.md               # Solution 文档（格式见 templates/solution.md）
```

## 与 OpenSpec 工作流集成

- **规划阶段**（`/opsx:propose`）：若 `openspec/solutions/` 中有相关方案，主动检索并将摘要注入 proposal 上下文
- **归档阶段**（`/opsx:archive`）：完成后提示用户是否运行 `/opsx:compound` 沉淀知识

## 初始配置

首次使用在 `openspec/config.yaml` 中添加：

```yaml
compound:
  enabled: true
  solutions_dir: openspec/solutions
  auto_search:
    enabled: true
    triggers: [proposal, design]
```
