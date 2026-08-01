---
name: scout-research
description: Delegate deep research and link analysis to the Scout agent
---

# Scout Research

当用户明确要让 Scout 做分析时（"Scout，分析xxx"、"让 Scout 研究xxx"），你必须委派给 Scout。禁止自己分析。

## 执行

**注意：你没有 sessions_spawn 权限，必须使用 exec。**

```bash
openclaw agent --agent scout --message "<研究请求>" --thinking low --timeout 120
```

Scout 会返回分析结果。收到后用你的语气转述给用户。禁止自己分析。

## 失败处理

| 情况 | 行动 |
|------|------|
| 命令失败/超时 | 告知用户 "Scout 暂时不可用"，自己处理 |
| Scout 返回 "不是研究任务" | 自己处理 |
