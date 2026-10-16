---
name: opsx:propose-enhanced
description: "增强的OpenSpec工作流集成说明：自动检索 solutions 知识库并注入上下文"
---

# OpenSpec + Compound 集成说明

本文档说明 Compound 能力如何与 OpenSpec 标准工作流集成。

## 集成点

### 1. 规划阶段（`/opsx:propose`）

执行时自动检索 `openspec/solutions/`：

1. 从变更名提取关键词（如 `add-user-authentication` → `authentication`、`user`）
2. 搜索 solutions 知识库，按相关性排序
3. 若找到相关方案（相关性 ≥ 0.6），将摘要注入 proposal 生成上下文：

```markdown
## Historical Context

Found 2 relevant solutions:

### JWT Authentication Patterns (95% match)
- Covers: token design, RS256, refresh rotation
- File: openspec/solutions/jwt-auth-patterns.md

Consider referencing this pattern in your proposal.
```

### 2. 继续阶段（`/opsx:continue`）

生成 design.md 或 tasks.md 时，根据 artifact 类型补充检索相关方案并注入。

### 3. 归档阶段（`/opsx:archive`）

完成后提示：

```
✅ 变更已归档。
💡 是否提取可复用方案？运行 /opsx:compound 沉淀知识。
[提取方案] [跳过]
```

## 配置

在 `openspec/config.yaml` 中启用：

```yaml
compound:
  enabled: true
  solutions_dir: openspec/solutions
  auto_search:
    enabled: true
    triggers: [proposal, design]
    min_relevance: 0.6
    max_solutions: 3
    injection_mode: summary   # summary | full | reference
  prompt_after_archive: true
```

### injection_mode 说明

| 模式 | 内容 | 适用场景 |
|------|------|---------|
| `summary` | 标题 + 关键要点 + 文件路径 | 默认，平衡上下文长度 |
| `full` | 完整 solution 内容 | 高相关性时，需要完整参考 |
| `reference` | 仅提示用户手动搜索 | 低 token 预算场景 |
