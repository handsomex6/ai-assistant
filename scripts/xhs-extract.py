#!/usr/bin/env python3
"""小红书笔记提取 → Obsidian Markdown
用法: python3 xhs-extract.py <小红书链接> [--obsidian-dir <vault路径>]
依赖: requests (pip install requests)
Cookie: ~/cookies.json (从 Chrome DevTools 导出)
"""

import glob
import json
import os
import re
import sys
import html
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, quote

COOKIE_FILE = Path.home() / "cookies.json"
OBSIDIAN_DIR = Path.home() / "Documents" / "Obsidian Vault" / "xhs"

def load_cookies():
    """加载 Cookie - 优先从 Chrome 数据库直接读取，失败时回退到 JSON 文件"""
    cookie_str = _load_from_chrome_db()
    if cookie_str:
        return cookie_str
    return _load_from_file()

def _load_from_chrome_db():
    """直接从 Chrome Cookie 数据库读取小红书 Cookie"""
    try:
        import sqlite3
        chrome_db = Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Cookies"
        if not chrome_db.exists():
            return None

        # 复制数据库避免锁定
        import shutil
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        tmp.close()
        shutil.copy2(chrome_db, tmp.name)

        conn = sqlite3.connect(tmp.name)
        rows = conn.execute("SELECT name, value FROM cookies WHERE host_key LIKE '%xiaohongshu%'").fetchall()
        conn.close()
        os.unlink(tmp.name)

        if rows:
            cookie_str = "; ".join(f"{name}={value}" for name, value in rows)
            return cookie_str
    except Exception:
        pass
    return None

def _load_from_file():
    """从 JSON 文件加载 Cookie（回退方案）"""
    if not COOKIE_FILE.exists():
        print(f"❌ Cookie 不存在。请确保 Chrome 已登录小红书。")
        sys.exit(1)

    try:
        with open(COOKIE_FILE) as f:
            text = f.read().strip()
        if text.startswith("["):
            cookies = json.loads(text)
            return "; ".join(f"{c['name']}={c['value']}" for c in cookies)
        else:
            pairs = {}
            for part in text.replace("\n", ";").split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    pairs[k.strip()] = v.strip()
            return "; ".join(f"{k}={v}" for k, v in pairs.items())
    except Exception as e:
        print(f"❌ Cookie 解析失败: {e}")
        sys.exit(1)

def fetch_note(url, cookie_str):
    """用 Cookie 请求小红书页面，提取 __INITIAL_STATE__"""
    import urllib.request
    import ssl

    # 绕过 SSL 验证问题
    ctx = ssl.create_default_context()

    # 桌面 UA 优先，失败时回退到 iPhone UA（新页面结构对移动端更友好）
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    ]

    html_content = None
    last_error = None
    for ua in user_agents:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", ua)
        req.add_header("Cookie", cookie_str)
        req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        req.add_header("Accept-Language", "zh-CN,zh;q=0.9")
        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                html_content = resp.read().decode("utf-8", errors="ignore")
            break
        except Exception as e:
            last_error = e
            continue

    if html_content is None:
        print(f"❌ 请求失败: {last_error}")
        sys.exit(1)

    # 提取 __INITIAL_STATE__
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*</script>', html_content, re.DOTALL)
    if not match:
        # 尝试另一种格式
        match = re.search(r'__INITIAL_STATE__\s*=\s*({.*?});', html_content, re.DOTALL)
    if not match:
        print("❌ 未找到 __INITIAL_STATE__，Cookie 可能已过期")
        sys.exit(1)

    json_str = match.group(1)
    # 处理特殊字符
    json_str = json_str.replace("undefined", "null")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        # 保存原始数据到文件供调试
        debug_file = Path.home() / "xhs-debug.json"
        with open(debug_file, "w") as f:
            f.write(json_str[:5000])
        print(f"📝 原始数据已保存到 {debug_file}")
        sys.exit(1)

def extract_note_data(state):
    """从 __INITIAL_STATE__ 提取笔记数据"""
    # 尝试多种可能的 JSON 路径
    note_data = None

    paths_to_try = [
        ["note", "noteDetailMap"],
        ["note", "currentNoteId"],
    ]

    note_detail_map = state.get("note", {}).get("noteDetailMap", {})
    if note_detail_map:
        note_id = list(note_detail_map.keys())[0]
        note_data = note_detail_map[note_id].get("note", {})

    if not note_data:
        # 新页面结构: noteData.data.noteData（iPhone UA 抓取时的路径）
        note_data = state.get("noteData", {}).get("data", {}).get("noteData", {})

    if not note_data:
        print("❌ 无法从页面数据中提取笔记内容")
        return None

    return note_data

def parse_note(note_data):
    """解析笔记字段"""
    result = {
        "note_id": "",
        "title": "",
        "content": "",
        "type": "normal",
        "author": "",
        "likes": 0,
        "collects": 0,
        "comments": 0,
        "tags": [],
        "images": [],
        "video_url": None,
        "publish_time": "",
    }

    result["note_id"] = note_data.get("noteId", note_data.get("id", ""))

    result["title"] = note_data.get("title") or note_data.get("displayTitle", "无标题")
    result["content"] = note_data.get("desc", "")
    result["type"] = note_data.get("type", "normal")

    # 作者
    user = note_data.get("user", {})
    result["author"] = user.get("nickname") or user.get("nickName", "未知")

    # 互动数据
    interact = note_data.get("interactInfo", {})
    result["likes"] = interact.get("likedCount", 0)
    result["collects"] = interact.get("collectedCount", 0)
    result["comments"] = interact.get("commentCount", 0)

    # 标签
    for tag in note_data.get("tagList", []):
        tag_name = tag.get("name", "")
        if tag_name:
            result["tags"].append(tag_name)

    # 图片
    for img in note_data.get("imageList", []):
        url_default = img.get("urlDefault") or img.get("url", "")
        if url_default:
            result["images"].append(url_default)

    # 视频
    video = note_data.get("video", {})
    if video:
        result["video_url"] = video.get("media", {}).get("stream", {}).get("h264", [{}])[0].get("masterUrl", "")

    # 发布时间
    time_val = note_data.get("time", 0)
    if time_val:
        dt = datetime.fromtimestamp(time_val / 1000)
        result["publish_time"] = dt.strftime("%Y-%m-%d")

    return result

def ocr_image(image_url, img_dir, index):
    """下载图片并用 macOS OCR 提取文字"""
    import subprocess
    import urllib.request

    img_path = img_dir / f"img_{index}.jpg"
    try:
        urllib.request.urlretrieve(image_url, img_path)
    except Exception:
        return ""

    # 用编译好的 Swift OCR 工具
    ocr_bin = Path(__file__).parent / "ocr"
    if not ocr_bin.exists():
        return ""

    try:
        result = subprocess.run([str(ocr_bin), str(img_path)], capture_output=True, text=True, timeout=30)
        text = result.stdout.strip()
        img_path.unlink(missing_ok=True)  # OCR 完删图片
        return text if text else ""
    except Exception:
        img_path.unlink(missing_ok=True)
        return ""

def transcribe_video(video_url, video_dir, note_title):
    """下载视频 → 提取音频 → whisper 转录"""
    import subprocess
    import urllib.request

    video_dir = Path(video_dir)
    video_dir.mkdir(parents=True, exist_ok=True)

    safe_title = note_title.replace("/", "-").replace(":", "-")[:30]
    video_path = video_dir / f"{safe_title}.mp4"
    audio_path = video_dir / f"{safe_title}.wav"

    # 1. 下载视频
    print(f"🎬 下载视频...")
    try:
        urllib.request.urlretrieve(video_url, video_path)
    except Exception as e:
        print(f"❌ 视频下载失败: {e}")
        return ""

    # 2. 提取音频
    print(f"🔊 提取音频...")
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(video_path), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(audio_path), "-y"],
            capture_output=True, check=True, timeout=120
        )
    except Exception as e:
        print(f"❌ 音频提取失败: {e}")
        return ""

    # 3. Whisper 转录
    print(f"📝 语音转录中...")
    try:
        result = subprocess.run(
            ["whisper", str(audio_path), "--model", "tiny", "--output_dir", str(video_dir), "--output_format", "txt"],
            capture_output=True, text=True, timeout=300
        )
        # 读取转录结果
        txt_files = sorted(glob.glob(str(video_dir / "*.txt")), key=os.path.getmtime, reverse=True)
        if txt_files:
            with open(txt_files[0], "r") as f:
                transcript = f.read().strip()
            print(f"✅ 转录完成: {len(transcript)} 字")
            # 清理大文件，只留转录文本
            video_path.unlink(missing_ok=True)
            audio_path.unlink(missing_ok=True)
            print(f"🧹 已清理视频和音频文件")
            return transcript
    except Exception as e:
        print(f"❌ 转录失败: {e}")

    return ""

def save_to_obsidian(note, obsidian_dir, video_transcript=""):
    """保存为 Obsidian Markdown 笔记，包括图片 OCR"""
    obsidian_dir = Path(obsidian_dir)
    obsidian_dir.mkdir(parents=True, exist_ok=True)

    # 图片文件夹
    img_dir = obsidian_dir / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    # 图片 OCR
    ocr_results = []
    if note["images"]:
        print(f"🔍 OCR 识别 {len(note['images'])} 张图片...")
        for i, img_url in enumerate(note["images"][:10]):  # 最多 10 张
            text = ocr_image(img_url, img_dir, i)
            if text:
                ocr_results.append(f"**图{i+1}**: {text}")
                print(f"  图{i+1}: {len(text)} 字")
        print(f"✅ OCR 完成: {len(ocr_results)}/{min(len(note['images']), 10)} 张识别到文字")

    # 文件名
    date_str = note["publish_time"] if note["publish_time"] else datetime.now().strftime("%Y-%m-%d")
    title = note["title"].replace("/", "-").replace(":", "-")[:50]
    filename = f"{date_str} {title}.md"
    filepath = obsidian_dir / filename

    content = f"""---
source: 小红书
note_id: {note['note_id']}
author: {note['author']}
date: {note['publish_time']}
type: {note['type']}
likes: {note['likes']}
collects: {note['collects']}
tags: {', '.join(note['tags'])}
status: extracted
---

# {note['title']}

## 📝 原文

{note['content']}

## 🔍 图片文字（OCR）

{chr(10).join(ocr_results) if ocr_results else '无'}

## 🎙️ 转录

{video_transcript if video_transcript else '无'}

## 📊 互动数据

❤️ {int(note['likes']):,} · ⭐ {int(note['collects']):,} · 💬 {int(note['comments']):,}

{' '.join(f'#{t}' for t in note['tags'])}

{chr(10).join(f'![]({img})' for img in note['images']) if note['images'] else ''}

---

## 📊 Scout 分析

（待分析）

---
*提取: {datetime.now().strftime("%Y-%m-%d %H:%M")} · 来源: 小红书 · 作者: {note['author']}*
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath

def main():
    if len(sys.argv) < 2:
        print("用法: python3 xhs-extract.py <小红书链接> [--obsidian-dir <路径>]")
        sys.exit(1)

    url = sys.argv[1]
    obsidian_dir = OBSIDIAN_DIR

    # 解析 --obsidian-dir
    for i, arg in enumerate(sys.argv):
        if arg == "--obsidian-dir" and i + 1 < len(sys.argv):
            obsidian_dir = Path(sys.argv[i + 1])

    print(f"🔗 链接: {url}")

    # 1. 加载 Cookie
    cookie_str = load_cookies()
    print("✅ Cookie 已加载")

    # 2. 请求页面
    state = fetch_note(url, cookie_str)
    print("✅ 页面数据已获取")

    # 3. 提取笔记
    note_data = extract_note_data(state)
    if not note_data:
        sys.exit(1)

    note = parse_note(note_data)
    print(f"📝 标题: {note['title']}")
    print(f"👤 作者: {note['author']}")
    print(f"💬 字数: {len(note['content'])}")
    print(f"🎬 类型: {'视频' if note['type'] == 'video' else '图文'}")

    # 3.5 去重：检查是否已提取过
    if note["note_id"]:
        import glob
        existing = glob.glob(str(obsidian_dir / f"*.md"))
        for fpath in existing:
            with open(fpath, "r") as f:
                first_lines = "".join(f.readline() for _ in range(15))
            if f"note_id: {note['note_id']}" in first_lines or note["note_id"] in first_lines:
                print(f"⏭️ 已存在，跳过: {fpath}")
                print(f"\n✅ 已有笔记: {fpath}")
                sys.exit(0)

    # 4. 视频转录（如果是视频）
    video_transcript = ""
    video_dir = obsidian_dir / "video"
    if note["type"] == "video" and note["video_url"]:
        video_transcript = transcribe_video(note["video_url"], video_dir, note["title"])

    # 5. 保存到 Obsidian
    filepath = save_to_obsidian(note, obsidian_dir, video_transcript)
    print(f"📁 已保存: {filepath}")

    # 5. 输出路径供后续使用
    print(f"\n✅ 完成！Scout 可读取: {filepath}")

if __name__ == "__main__":
    main()
