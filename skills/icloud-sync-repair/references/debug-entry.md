# 项目内 Debug 入口

三类动作分开命名，避免“修复”按钮掩盖实际副作用：

1. **只读诊断**：显示真实签名环境/容器、账号状态、目标 zone 状态、同步阶段及结构化错误。普通客户端无法读取完整服务端 schema；读到一条记录不能证明未使用字段存在。
2. **补齐 Development 字段**：必须同时满足编译期 DEBUG、实际签名环境恰为 Development、非 preview/smoke/isolated test、账号可用，并由用户确认当前容器和写操作。运行时不能通过文字输入/下拉框把 Production 伪装成 Development。
3. **立即重试同步**：只走已有 coordinator/retry 入口，保留 outbox、checkpoint 和用户开关，继续遵守限流。它不是 schema 修复，也不应在同步关闭时偷偷开启同步。

开发初始化使用全新、随机命名的独立诊断 zone，使用所有需要的 record type 和字段类型，给每个可选/加密/Asset 字段写非空合成值。用小型临时文件构造 Asset，不能拿真实剪贴板作测试。检查批量保存的每条结果，成功与失败都尝试清理本次 zone 和本地临时文件；网络超时造成结果不确定时报告遗留 zone，不能宣称已清理。清理 zone 不撤销已创建的 schema 字段。

若业务使用 `CKSyncEngine.automaticallySync`，先确认事件处理在解码前忽略非业务 zone。仅给显式 `fetchChanges` 传 zone scope，不等于自动同步永远只拉该 zone；诊断控制记录不能触发业务的未知协议/升级错误。增加离线测试证明合成记录不会进入真实同步 reducer。

字段类型冲突、索引、权限、Production 部署和数据迁移不由此入口修复；引导导出 schema 并在 Console 审查。生产签名的 Debug 包只能诊断/重试，发布构建不编译初始化 API/UI。客户端不得携带管理凭据。

## Momonga 案例（不是其他项目的默认字段契约）

2026-10-16，Production 中 Clip 保存返回 `invalidArguments`，批次 `partialFailure`。核对实际签名与两套导出发现缺少：

| Record Type | 字段 | 类型 |
| --- | --- | --- |
| Clip | deletionEnvelope | ENCRYPTED BYTES |
| Clip | payloadAsset | ASSET |
| LibraryControl | resetRequestID | STRING |

编码会对未使用字段赋 nil，且只有大正文才使用 Asset；仅靠普通文本试跑不足以覆盖所有字段。三个字段一起补齐并部署后，原进程恢复 idle。此证据支持 schema 缺项根因，但没有单独隔离证明哪一个字段造成每次失败。不要把这三个字段当作通用的 iCloud 修复列表。

持续预防：维护客户端字段契约；离线测试初始化记录与基线字段/加密类型一致；发布前比较真实 Development 和 Production 导出。初始化成功并不验证索引/权限、双设备冲突、APNs 或真实删除路径。
