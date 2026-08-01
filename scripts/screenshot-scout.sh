#!/bin/bash
# 截图 → OCR → 发给 Scout 分析
# 用法: ./screenshot-scout.sh 或绑快捷键

set -euo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_IMG=$(mktemp -t scout-screenshot.XXXXXX.png)

# 1. 截屏（选区模式）
echo "📸 请选择截图区域..."
screencapture -i "$TMP_IMG"

# 检查是否真的截了图
if [ ! -s "$TMP_IMG" ]; then
    rm -f "$TMP_IMG"
    exit 0
fi

# 2. OCR 提取文字
echo "🔍 识别文字中..."
TEXT=$("$SCRIPT_DIR/ocr" "$TMP_IMG" 2>/dev/null)

if [ -z "$TEXT" ]; then
    osascript -e 'display notification "未识别到文字" with title "📸 Scout OCR"'
    rm -f "$TMP_IMG"
    exit 0
fi

# 3. 发送给 Scout（后台）
echo "$TEXT" | openclaw agent \
    --agent main \
    --message "Scout，帮我分析这张截图中的小红书内容：

$TEXT" \
    --thinking low \
    --timeout 120 \
    > /dev/null 2>&1 &

# 4. 通知用户
osascript -e "display notification \"已发送给 Scout 分析\" with title \"📸 Scout OCR\" subtitle \"识别到 $(echo "$TEXT" | wc -l) 行文字\""

# 5. 清理
rm -f "$TMP_IMG"
