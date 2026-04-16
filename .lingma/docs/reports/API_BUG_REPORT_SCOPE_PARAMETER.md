# Lingma API Bug报告

## Bug描述
`update_memory` API的`scope`参数设置不生效

## 复现步骤
1. 调用`update_memory(action="update", scope="global", ...)`
2. API返回`success`
3. 在Lingma界面查看记忆,仍显示"当前项目"而非"全局"

## 影响范围
- 所有通过`update_memory`设置的记忆scope
- 可能导致知识无法跨项目共享

## 当前状态
- ✅ 已在`.lingma/rules/memory-usage.md`中记录此问题
- ✅ 已建立人工审核机制
- ❌ 等待Lingma官方修复

## 建议修复方案
1. 修复`update_memory` API的scope参数处理逻辑
2. 或提供新的API专门用于修改记忆scope
3. 或在UI中明确显示记忆的实际scope状态

## 临时解决方案
- 用户手动通过Lingma界面修改记忆scope
- 或联系技术支持获取帮助

## 报告时间
2026-04-15

---
**状态**: 已确认,等待修复