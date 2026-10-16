---
name: opsx:compound
description: "从已完成的OpenSpec变更中提取可复用的解决方案，沉淀到知识库"
argument-hint: "[optional: 变更名称，默认为当前或最近完成的变更]"
---

# /opsx:compound

从已完成的 OpenSpec 变更中提取可复用的技术方案、模式和经验教训，保存到 `openspec/solutions/`。

## 使用时机

- 变更完成后（`/opsx:apply` 之后，`/opsx:archive` 之前或之后）
- 解决了值得记录的复杂问题或发现了可复用的架构模式时

## 执行流程

### Phase 1：分析变更

1. 定位变更目录：提供了变更名则用 `openspec/changes/{name}/`，否则查找最近完成的变更
2. 读取 `proposal.md`（理解问题）、`design.md`（获取方案）、`tasks.md`（了解实现步骤）
3. 识别可复用内容：核心技术方案、关键决策、可复用模式、经验教训

### Phase 2：展示建议并由用户确认

```
分析完成，发现以下可复用内容：

┌─────────────────────────────────────────────────────────┐
│ 1. [架构模式] 微服务认证网关设计                          │
│    问题：统一认证入口，支持多种认证方式                    │
│    方案：JWT + API Key双模式，网关层统一验证               │
│    价值：高（可复用于其他服务）                           │
└─────────────────────────────────────────────────────────┘

请选择要记录的内容：[1] [2] [全部] [跳过]
```

### Phase 3：生成 Solution 文档

对每个选中的内容：

1. 确定文件名（`{category}-{brief-description}.md`，kebab-case，含类别前缀如 `architecture-`、`security-`、`performance-`）
2. 使用 `templates/solution.md` 填充：问题描述、解决方案、代码示例、适用场景、经验教训
3. 询问是否关联关键代码文件（repo-relative 路径）

### Phase 4：保存并更新索引

1. 写入 `openspec/solutions/{filename}.md`
2. 更新 `openspec/solutions/_index.json`
3. 确认完成：

```
✅ 已生成解决方案：
- openspec/solutions/architecture-auth-gateway-design.md

这些方案将在未来的规划中被自动检索。
```

## 注意事项

- 最佳时机：变更完成但尚未归档（也可在归档后从 archive 目录读取）
- 不是所有变更都值得记录，重点关注复杂问题、新模式、重要教训
- 关联代码时选关键实现文件，而非测试或配置

## 相关命令

- `/opsx:compound-search` — 搜索已有解决方案
- `/opsx:compound-refresh` — 整理和更新 solutions 目录
