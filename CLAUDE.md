# AI Assistant

基于 OpenClaw 的个人 AI 多 Agent 系统。

## 架构

```
微信 / Telegram / WhatsApp
           │
      Alex (main) — 唯一入口
           │
           ├─ 日常/Inbox/对话 → 自己处理
           └─ 研究分析 → sessions_send → Scout
```

- **Alex (main)**：总管，Inbox + 对话 + 调度
- **Scout**：研究员，小红书提取 + OCR + Whisper + 分析

## 目录

```
ai-assistant/
├── acquisition/          ← 数据层（inbox / overview / sources）
├── workspaces/alex/      ← Alex 工作区
├── workspaces/scout/     ← Scout 工作区
└── scripts/              ← 工具脚本
```

## 技术栈

- OpenClaw 2026.7.1-2
- DeepSeek v4-flash
- whisper (OpenAI) + macOS Vision OCR

## 入口

| 入口 | 方式 |
|------|------|
| 💬 微信 | 已连接 |
| 📱 Telegram | @Chiplusdaybot |
| 💚 WhatsApp | work 号 |
| 🌐 网页 | http://127.0.0.1:18789/ |
| ⌨️ 桌面 | `scripts/send-inbox.sh` |

## 使用方式

- 日常：直接发消息，Alex 自动判断 Inbox 还是对话
- 研究：发 "Scout，分析xxx" 或发链接
- 存入/舍弃：Scout 分析完会问
