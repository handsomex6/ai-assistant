#!/bin/bash
# Personal Inbox Agent - 桌面快捷输入
# 弹出对话框，通过 stdin 传值避免 AppleScript 注入

set -euo pipefail
export PATH="$HOME/.npm-global/bin:$PATH"
LOG_FILE="$HOME/Library/Logs/send-inbox.log"

# 弹出输入框，通过 stdin 传参给 osascript
INPUT=$(osascript <<'APPLESCRIPT' 2>/dev/null
display dialog "记录什么？" default answer "" with title "📥 Inbox" buttons {"取消", "记录"} default button "记录" cancel button "取消"
text returned of result
APPLESCRIPT
)

# 用户点了取消或没输入
if [ -z "$INPUT" ]; then
    exit 0
fi

# 发给 Agent（后台运行）
openclaw agent \
    --agent main \
    --message "Inbox: ${INPUT}" \
    --thinking low \
    --timeout 60 \
    >> "$LOG_FILE" 2>&1 &

AGENT_PID=$!

# 显示通知（参数化避免注入）
osascript - "$INPUT" <<'APPLESCRIPT' 2>/dev/null
on run argv
    set inputText to item 1 of argv
    display notification "已记录: " & inputText with title "📥 Inbox" subtitle "Agent 处理中…"
end run
APPLESCRIPT

# 短暂等待，如果 Agent 启动失败则通知
sleep 2
if ! kill -0 $AGENT_PID 2>/dev/null; then
    osascript - "$INPUT" <<'APPLESCRIPT' 2>/dev/null
    on run argv
        display notification "发送失败，请检查日志" with title "📥 Inbox 错误" subtitle "Agent 未启动"
    end run
APPLESCRIPT
fi
