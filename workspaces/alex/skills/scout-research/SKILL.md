---
name: scout-research
description: Delegate deep research and link analysis to the Scout agent
---

# Scout Research

当用户明确要让 Scout 做分析时（"Scout，分析xxx"、"让 Scout 研究xxx"），你必须委派给 Scout。禁止自己分析。

## 执行

使用 `sessions_send(agent: "scout", message: "<研究请求>")` 委派（⚠️ 不要用 sessions_spawn，已损坏）。

Scout 返回后，用你的语气转述结果，末尾问「存入还是舍弃？」。禁止自己分析。

## 失败处理

| 情况 | 行动 |
|------|------|
| Scout 超时 | 告知用户 "Scout 卡住了，要不直接告诉我内容我帮你看？" |
| Scout 返回 "不是研究任务" | 自己处理 |
| sessions_send 失败 | 降级自己处理 |
