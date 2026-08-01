# AI Assistant

基于 OpenClaw 的个人 AI 多 Agent 系统。

## 架构

```
微信 / Telegram
      │
   Alex (main agent) — 唯一入口
      │
      ├─ 日常/Inbox/对话 → 自己处理
      └─ 研究分析 → sessions_spawn → Scout agent
```

- **Alex (main)**：总管，Inbox + 对话 + 调度
- **Scout**：研究分析专家，独立 workspace

## 技术栈

- OpenClaw 2026.7.1-2
- DeepSeek v4-flash

## 入口

| 入口 | 方式 |
|------|------|
| 📱 Telegram | @Chiplusdaybot |
| 💬 微信 | 已连接 |
| 🌐 网页 | http://127.0.0.1:18789/ |
| ⌨️ 桌面 | `scripts/send-inbox.sh` |

## 使用方式

- 日常：直接发消息，Alex 自动判断 Inbox 还是对话
- 研究：发 "Scout，分析xxx" 或发链接，Alex 委派给 Scout
