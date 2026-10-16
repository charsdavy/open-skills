---
name: opsx:compound-refresh
description: "整理和更新solutions目录，重建索引，清理过时内容"
argument-hint: "[--check-links] [--merge-duplicates] [--archive-stale] [--dry-run]"
---

# /opsx:compound-refresh

维护 `openspec/solutions/` 知识库健康状态，包括重建索引、修复代码链接、检测重复、标记过时内容。

## 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `--check-links` | 检查并修复代码文件链接 | 开启 |
| `--merge-duplicates` | 检测并提示合并重复方案 | 关闭 |
| `--archive-stale` | 标记超过90天未引用的方案 | 关闭 |
| `--dry-run` | 预览变更但不实际执行 | 关闭 |

## 执行流程

### Phase 1：扫描并重建索引

扫描 `openspec/solutions/*.md`，从 frontmatter 提取元数据，生成新的 `_index.json`：

```json
{
  "version": "1.0.0",
  "lastUpdated": "2026-04-24T10:30:00Z",
  "stats": { "total": 15, "active": 12, "deprecated": 2, "superseded": 1 },
  "entries": { "jwt-auth-patterns": { "title": "...", "tags": [...], "status": "active" } },
  "tagIndex": { "authentication": ["jwt-auth-patterns", "oauth-integration"] }
}
```

### Phase 2：代码链接检查（`--check-links`）

验证 `related_code` 中的文件路径是否存在，对失效链接提供修复建议：

```
❌ src/utils/token.ts → 不存在
   建议：src/utils/token-helper.ts（通过 git 历史发现）
```

### Phase 3：重复检测（`--merge-duplicates`）

计算方案间相似度，展示高相似度对并询问合并策略：

```
相似度 85%：
  jwt-authentication.md (2026-01-15) ↔ jwt-auth-patterns.md (2026-02-01)
建议：以较新的为基础，整合独特内容
[合并] [保留两者] [查看详情]
```

### Phase 4：过时检测（`--archive-stale`）

列出超过90天未更新且可能过时的方案，询问状态处理：

```
⚠️ legacy-webpack-config.md（180天）— 建议标记为 deprecated
[标记废弃] [保持active] [查看详情]
```

### Phase 5：输出报告

```
┌─────────────────────────────────────────────────────────┐
│ Compound Refresh 完成                                    │
├─────────────────────────────────────────────────────────┤
│ 扫描：15 个方案 | 索引已更新                             │
│ 链接：42/45 有效，3 个失效（建议修复）                  │
└─────────────────────────────────────────────────────────┘
```

## 交互示例

### 标准刷新

```
用户: /opsx:compound-refresh

AI: 扫描 15 个文件 ✓ → 重建索引 ✓ → 检查 45 个链接（3 个失效）

    ⚠️ 发现 3 个失效链接，运行 /opsx:compound-refresh --check-links 修复。
```

### 预览模式

```
用户: /opsx:compound-refresh --merge-duplicates --dry-run

AI: 🔍 预览模式（不修改文件）
    检测到 1 对重复（85%相似度）：jwt-authentication.md ↔ jwt-auth-patterns.md
    实际执行：/opsx:compound-refresh --merge-duplicates
```

## 相关命令

- `/opsx:compound` — 创建新的 solution
- `/opsx:compound-search` — 搜索 solutions
