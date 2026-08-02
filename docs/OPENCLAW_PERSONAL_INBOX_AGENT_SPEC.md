# OpenClaw Personal Inbox Agent Specification

> ⚠️ **历史文档**：原始设计规格书。实际实现已演进为 `ai-assistant` 项目，架构差异见下方。

## 原始目标 vs 实际实现

| | 原始设计 | 实际实现 |
|------|------|------|
| 项目名 | personal-inbox-agent | **ai-assistant** |
| 数据层 | `second-brain/`（在 Alex workspace 下） | **`acquisition/`**（独立于 Agent） |
| Agent 数 | 1（Alex 全干） | **2**（Alex 总管 + Scout 研究员） |
| 渠道 | Obsidian 展示 | **微信 + Telegram + WhatsApp** |
| 小红书 | 不支持 | **提取 + OCR + Whisper 转录** |
| 展示 | dashboard.md | **overview.md** |

以下为原始规格书内容（仅供参考）。

# 1. 项目目标

创建一个基于 OpenClaw 的个人 AI Inbox 系统。

目标：

用户可以随时输入：

- 想法
- 待办事项
- 想研究的问题
- 临时灵感
- 未来计划

AI 自动理解内容，并维护一个实时 Markdown Dashboard。

最终效果：

用户打开桌面即可看到：

- 当前关注事项
- 下一步行动
- 待研究内容
- 想法池

# 2. 核心架构

```
用户输入
    ↓
OpenClaw Agent
    ↓
Inbox Manager Skill
    ↓
Markdown 文件系统
    ↓
Obsidian Dashboard 展示
```

# 3. MVP 范围

只实现以下功能：

## 输入

支持文本输入。

示例：

```
Inbox:
想研究 Claude Code 和 Codex 如何协作开发
```

## AI分类

Agent 自动判断：

- Task（任务）
- Idea（想法）
- Research（研究）
- Project（项目）
- Reminder（提醒）

## 文件管理

维护：

```
second-brain/

├── dashboard.md
├── inbox.md
├── ideas.md
├── projects.md
└── archive.md
```

# 4. 开发阶段

# Phase 0：环境准备

## 目标

确认 OpenClaw 可以运行。

检查：

- Git
- Node.js
- npm/pnpm
- Python（如需要）

验证：

```
git --version

node -v

npm -v
```

# Phase 1：安装并初始化 OpenClaw

## 目标

完成：

- OpenClaw安装
- Workspace初始化
- Agent可启动

验收：

满足：

```
openclaw --version
```

可以正常返回版本。

# Phase 2：创建 Workspace

创建：

```
workspace/

├── AGENTS.md
├── skills/
└── second-brain/
```

# Phase 3：创建第二大脑目录

创建：

```
second-brain/

├── dashboard.md
├── inbox.md
├── ideas.md
├── projects.md
└── archive.md
```

## dashboard.md 模板

```
# 🧠 Personal Dashboard


## 🔥 当前关注

暂无


## 📌 下一步行动

暂无


## 🔍 待研究

暂无


## 💡 想法池

暂无


## 🚧 项目

暂无
```

## inbox.md

用于保存原始输入：

```
# Inbox
```

# Phase 4：创建 Inbox Manager Skill

路径：

```
skills/

└── inbox-manager/

    └── SKILL.md
```

SKILL.md：

```
---
name: inbox-manager
description: Manage user's personal inbox and dashboard
---

# Personal Inbox Manager


你的职责：

管理用户的个人 Inbox。


收到输入后：

1. 判断类型：

- Task
- Idea
- Research
- Project
- Reminder


2. 保存原始内容到：

inbox.md


3. 更新：

dashboard.md


4. 根据需要更新：

ideas.md

projects.md


规则：

- 不删除用户输入
- 不遗漏信息
- 不过度总结
- 优先产生行动项
- Dashboard保持简洁
```

# Phase 5：配置 Agent 行为

修改：

```
AGENTS.md
```

加入：

```
你是用户的 Personal Inbox Agent。

主要职责：

帮助用户管理个人想法和行动。

当用户输入：

Inbox:
xxx

默认执行：

1. 分类
2. 保存
3. 更新Dashboard


不要输出长篇解释。
优先执行文件更新。
```

# Phase 6：功能测试

## 测试1：Idea

输入：

```
Inbox:
想做一个医学AI助手
```

期待：

dashboard.md:

```
## 💡 想法池

- 医学AI助手
```

## 测试2：Research

输入：

```
Inbox:
研究Claude Code和Codex协作开发
```

期待：

dashboard.md:

```
## 🔍 待研究

- Claude Code和Codex协作开发
```

## 测试3：Task

输入：

```
Inbox:
周末安装OpenClaw
```

期待：

dashboard.md:

```
## 📌 下一步行动

- 安装OpenClaw
```

# Phase 7：桌面展示

第一版：

使用 Obsidian。

打开：

```
second-brain/dashboard.md
```

要求：

- 文件变化可以实时刷新
- Dashboard长期打开
- 用户随时查看状态

# MVP验收标准

完成后：

用户输入：

```
Inbox:
想研究AI Agent自动化
```

系统自动：

1. 接收输入
2. 判断类型
3. 写入 inbox.md
4. 更新 dashboard.md
5. Obsidian显示变化

满足以上条件，即完成第一版。

# 后续扩展（不要在MVP实现）

## 输入渠道

未来增加：

- Telegram
- 飞书
- 快捷键输入
- 语音输入

## AI能力

未来增加：

- 每日总结
- 每周规划
- 自动排序优先级
- 项目拆解

## 信息来源

未来增加：

- ChatGPT对话整理
- Claude对话整理
- 小红书内容整理
- 网页收藏整理

## 高级能力

未来增加：

- 多Agent
- RAG知识库
- 自动执行任务

# 开发原则

1. 优先完成可运行MVP。
2. 不提前开发复杂功能。
3. 保持数据为Markdown，避免锁定平台。
4. 所有用户数据必须可读取、可迁移。
5. Agent应该像个人秘书，而不是聊天机器人。