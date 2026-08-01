---
name: xhs-extract
description: Extract Xiaohongshu post content and save to Obsidian markdown
---

# 小红书提取

当用户发送小红书链接时，使用此工具提取内容到 Obsidian。

## 执行

```bash
python3 ~/Documents/ai-assistant/scripts/xhs-extract.py "<链接>" --obsidian-dir ~/Documents/Obsidian\ Vault/xhs
```

脚本会：
1. 从 Chrome 数据库自动读取 Cookie
2. 请求页面提取内容（标题、正文、图片、标签）
3. 保存为 Obsidian Markdown 笔记
4. 输出保存路径

## 提取后

如果用户要求分析，通知 Scout 读取生成的 Obsidian 文件：

```
Scout，读取 <文件路径> 并分析
```
