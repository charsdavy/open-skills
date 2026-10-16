---
name: icloud-sync-repair
description: 排查和修复 Apple 平台应用的 iCloud/CloudKit 同步失败，结合设备日志、实际签名、客户端编码字段和云端 schema 定位缺字段、类型或加密属性不一致、环境部署遗漏等问题。适用于同步配置异常、CKError、Development 正常但 Production 失败，以及需要补字段、部署 schema 或设计 Debug 修复入口的请求。
---

# iCloud Sync Repair

以“实际运行产物 → 原始失败 → 客户端字段契约 → 真实云端导出 → 最小修复 → 原环境复测”形成证据闭环。用户已登录 iCloud 或过去曾缺字段，都不能代替本次诊断。

## 定位

1. 确认项目、运行设备、App 路径/版本、时间窗口、实际签名的 Team、容器、环境和数据库作用域。Debug 不一定是 Development，Release/TestFlight 应核对实际 Production 签名。先读取项目指令和已有修复记录。
2. 获取应用/设备日志，找到最早失败的操作及原始 `CKError`；递归检查 `partialFailure` 子错误和 underlying error。区分账号、权限/签名、网络/限流、schema、冲突及本地存储问题。日志被隐去时明确证据缺口，不从一个 `code=12` 推断具体字段。
3. 从编码/解码代码列出所有 record type、普通字段、`encryptedValues` 字段、类型、Asset 和索引要求；包括可选、赋 nil、大正文、墓碑、重置/控制记录等分支。赋 nil 可能仍产生 changed key，小文本成功不能证明 schema 完整。
4. 从正确 Team/container 的 Console 或已配置管理凭据的工具分别导出 Development、Production schema。对照当前客户端契约；仓库基线通过不等于云端通过。字段比较可用：

   ```sh
   python3 <skill-dir>/scripts/compare_schema.py --expected <client-baseline.ckdb> --actual <fresh-cloud-export.ckdb>
   ```

   脚本只比较所需 record type、字段和类型（包括加密），容许额外字段；索引、权限和部署差异须另审。没有可靠基线时先从代码建立并审查，不从旧云端导出盲目复制。

操作命令、错误分流及设备限制见 [排查手册](references/runbook.md)。

## 修复

- 客户端错误：修正字段名称、类型或编码方式并加离线回归；不要为迁就错误代码往生产 schema 加错字段。
- Development 缺字段：审查完整差异后，在 Console 添加正确类型，或使用项目内有环境门禁的 Debug 合成记录入口初始化。已有字段类型/加密属性冲突不能靠重复保存修复，应停止并设计兼容迁移。
- Production 缺字段：先补 Development，再审查 **全部**待部署差异；会夹带其他人的改动时停止。展示容器、环境、增加的字段/类型以及不可撤销性，取得本次生产部署的明确授权后再部署，最后重新导出 Production 校验。
- 普通客户端 CloudKit API 不能部署 Production schema。不得把管理 token/开发者凭据嵌入应用，或承诺“一键修复全部 iCloud 问题”。没有管理权限时提供精确变更单，不反复重试相同写入。
- 本任务的修复授权不等于清库授权。禁止把 Reset Environment、删现有 zone/记录、退出账号、清本地 outbox/checkpoint 当作常规修复。Debug 初始化只可清理本次新建且独占的诊断 zone；清理失败须报告 zone 名，不扩大删除范围。

## 验证与交付

重新导出并验证云端 schema；在原安装包/原账号/原环境验证失败操作恢复，保留前后时间线。只有 schema 校验通过时，不宣称真实同步已恢复。明确短文本、Asset、删除、双设备、APNs 等哪些已测、哪些未测。

把字段基线、离线校验、测试和发布门禁纳入项目，避免以后只跑普通文本就漏字段。报告区分事实、推断和未验证事项；不提交账号标识、剪贴板内容、token 或完整私人日志。

项目内 Debug 入口设计及一次真实案例见 [Debug 安全边界](references/debug-entry.md)。
