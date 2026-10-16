---
name: opsx:compound-search
description: "搜索OpenSpec解决方案知识库"
argument-hint: "<搜索关键词> [--tag=<标签>] [--status=active|all] [--limit=<数量>]"
---

# /opsx:compound-search

搜索 `openspec/solutions/` 中的历史解决方案，快速找到可复用的技术方案、模式和最佳实践。

## 参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `query` | 搜索关键词 | `authentication`、`"react performance"` |
| `--tag` | 按标签过滤 | `--tag=security` |
| `--status` | 按状态过滤 | `--status=active`（默认） |
| `--limit` | 限制结果数量 | `--limit=5` |

## 执行流程

### Phase 1：解析查询

从参数中提取关键词和过滤条件。

### Phase 2：加载索引

读取 `openspec/solutions/_index.json`，若不存在则直接扫描 solutions/ 目录。

### Phase 3：多维度匹配，按相关性排序

搜索维度（优先级从高到低）：
1. 标题匹配
2. 标签匹配
3. 全文内容匹配
4. 文件名匹配
5. 关联代码路径匹配

### Phase 4：格式化输出

```
找到 3 个相关解决方案：

┌─────────────────────────────────────────────────────────┐
│ 1. JWT认证实现模式 (95%匹配) ⭐                          │
│    🏷️  authentication, jwt, security                   │
│    📅  2026-01-15 | ✅ active                           │
│    📝  实现安全的用户认证机制，支持Token生成与验证...    │
└─────────────────────────────────────────────────────────┘

操作：[查看1] [查看2] [在规划中引用]
```

## 无结果时的处理

```
未找到匹配的解决方案。

建议：
1. 尝试更通用的关键词，如 "api" 或 "backend"
2. 当实现该功能后，记得用 /opsx:compound 记录经验
```

## 在规划中手动引用

```
用户: /opsx:compound-search react state management
AI: [显示搜索结果]

用户: 在规划中引用第1个
AI: 已将 "React Context最佳实践" 添加到 proposal 上下文。
```

## 相关命令

- `/opsx:compound` — 从变更创建新的 solution
- `/opsx:compound-refresh` — 重建索引
