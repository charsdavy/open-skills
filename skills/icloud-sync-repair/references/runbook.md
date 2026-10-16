# 排查手册

## 先固定实际产物

macOS 示例，替换 App 路径、subsystem 和时间窗口；不要用源码 entitlements 代替实际签名：

```sh
codesign -d --entitlements :- /Applications/Example.app
codesign -dv /Applications/Example.app
/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' /Applications/Example.app/Contents/Info.plist
/usr/bin/log show --last 20m --style compact --info --debug \
  --predicate 'subsystem == "com.example.app"'
```

核对 `com.apple.developer.icloud-container-identifiers`、`icloud-container-environment`、`icloud-services` 和 Team。日志查询保持短时间窗/目标 App 范围；避免采集整台设备的私人日志。沙盒文件日志被 TCC 拦截时可尝试 unified log，但不能绕过权限。

iOS/iPadOS 使用当前环境可用的 Xcode/devicectl 或设备工具读取对应 App 日志；先查询设备和命令帮助，不猜设备 ID。设备锁屏时请求解锁，用户已确认解锁后重新检查一次实际状态，不陷入重复询问。Simulator 不证明真机签名或 APNs 正常。

## 错误分流

| 证据 | 下一步 |
| --- | --- |
| `partialFailure` | 展开每条失败记录对应的子错误，保留操作/record type，不仅记录外层 code=2 |
| `invalidArguments` / `serverRejectedRequest` | 检查原始描述、字段契约、实际云端 schema；也可能是无效请求、Asset 或记录构造错误 |
| `badContainer` / `missingEntitlement` | 对照运行产物签名、profile、容器归属和真实环境 |
| `notAuthenticated` / 账号不可用 | 检查 `accountStatus`、设备登录和系统限制；不自动退出账号 |
| `networkFailure` / `serviceUnavailable` / `requestRateLimited` | 遵守 retry-after，确认网络和服务状态，不以加字段处理 |
| `serverRecordChanged` | 检查冲突合并和 change tag，不改 schema |
| `zoneNotFound` / `unknownItem` | 区分预期首次启动和丢 zone；按已有恢复协议处理，不直接清库 |

原始错误描述可能含记录名/账号标识。仅在本地诊断 UI 显示或经用户检查后分享；持久化/公开日志使用脱敏结构。不要把字段内容、加密载荷或 CKRecord 整体打印到日志。

## 导出、补字段、部署

- 首选已登录的 CloudKit Console；也可使用已有配置的 `cktool`，先读 `xcrun cktool --help`。没有管理 token 不等于可以搜索用户凭据或将凭据写入项目。
- 选择 Team → container → Development/Production，分别留存原始 `.ckdb`。Console 的日志导出不一定包含设备当前的保存失败，不能据此捏造拒绝原因。
- 普通 `Data` 和 `encryptedValues` 的 `ENCRYPTED BYTES` 不等价；`CKAsset` 是 `ASSET`，不能替换为 STRING/BYTES。按代码确认 LIST、REFERENCE、TIMESTAMP、数值类型等。
- 添加所需字段，不删除云端额外字段，不擅自变更原有索引/权限。生产字段类型不可随意改，兼容迁移需要新字段和读写过渡方案。
- 生产部署会合并所有待部署 schema 变更，可能不是只部署当前 record type。先审查完整 diff，再获得明确授权。部署后导出并核验实际 Production，而非只看成功 toast。
- 失败后按新错误定位，不循环部署、不重复建 zone、不靠不断重试吞掉错误。

Apple 官方说明（2026-10 核对）：[Deploying an iCloud Container’s Schema](https://developer.apple.com/documentation/cloudkit/deploying-an-icloud-container-s-schema)。开发 schema 可增加字段；部署将类型、字段、索引合并到生产，不复制记录，且需要开发者管理权限。
