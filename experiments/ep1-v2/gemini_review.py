#!/usr/bin/env python3
"""呼叫 Gemini 扮演「奇幻輕小說愛好者鄉民」的評審。
用法: python3 gemini_review.py <persona_file> <story_file> <out_file>
"""
import json
import os
import sys
import urllib.request

API_KEY = os.environ["GEMINI_API_KEY"]  # export GEMINI_API_KEY=... 再執行，勿把金鑰寫進版控
MODEL = "gemini-3.6-flash"  # 此金鑰下可呼叫的最強模型（Pro 系列 free-tier 配額為 0）
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"


def main():
    persona_file, story_file, out_file = sys.argv[1], sys.argv[2], sys.argv[3]
    persona = open(persona_file, encoding="utf-8").read()
    story = open(story_file, encoding="utf-8").read()
    prompt = persona + "\n\n=== 以下是要評的稿子 ===\n\n" + story

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 1.0, "maxOutputTokens": 8192},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.load(resp)

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        text = "[呼叫失敗] " + json.dumps(result, ensure_ascii=False, indent=2)

    open(out_file, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
