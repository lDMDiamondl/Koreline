"""
CelesteKRPatch 새 릴리즈 감지 → Discord 알림 봇
새 릴리즈가 올라오면 릴리즈 URL 하나만 전송합니다.
"""

import os
import json
import urllib.request
import urllib.error

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────
GITHUB_REPO       = os.getenv("GITHUB_REPO", "lDMDiamondl/CelesteKRPatch")
DISCORD_WEBHOOK   = os.getenv("DISCORD_WEBHOOK_URL", "")
LAST_RELEASE_FILE = os.getenv("LAST_RELEASE_FILE", "last_release.txt")

GITHUB_API_URL    = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


# ──────────────────────────────────────────────
# GitHub API 호출
# ──────────────────────────────────────────────
def fetch_latest_release() -> dict:
    req = urllib.request.Request(
        GITHUB_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "CelesteKRPatch-ReleaseBot/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[ERROR] GitHub API 오류: HTTP {e.code}")
        raise
    except Exception as e:
        print(f"[ERROR] 네트워크 오류: {e}")
        raise


# ──────────────────────────────────────────────
# 마지막 알림 릴리즈 ID 관리
# ──────────────────────────────────────────────
def load_last_release_id() -> str:
    try:
        with open(LAST_RELEASE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def save_last_release_id(release_id: str):
    with open(LAST_RELEASE_FILE, "w", encoding="utf-8") as f:
        f.write(release_id)
    print(f"[INFO] 마지막 릴리즈 ID 저장: {release_id}")


# ──────────────────────────────────────────────
# Discord 전송 (URL만)
# ──────────────────────────────────────────────
def send_discord_message(url: str):
    if not DISCORD_WEBHOOK:
        print("[ERROR] DISCORD_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        raise ValueError("DISCORD_WEBHOOK_URL 없음")

    payload = json.dumps({"content": url}).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[INFO] Discord 전송 성공: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[ERROR] Discord Webhook 오류: HTTP {e.code} — {body}")
        raise


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────
def main():
    print(f"[INFO] GitHub 릴리즈 확인 중: {GITHUB_REPO}")

    release    = fetch_latest_release()
    release_id = str(release["id"])
    tag        = release.get("tag_name", "?")
    html_url   = release.get("html_url", "")
    last_id    = load_last_release_id()

    print(f"[INFO] 최신 릴리즈: {tag} (ID: {release_id})")
    print(f"[INFO] 마지막 알림 ID: {last_id or '(없음 — 최초 실행)'}")

    if release_id == last_id:
        print("[INFO] 새 릴리즈 없음. 종료합니다.")
        return

    print(f"[INFO] 새 릴리즈 감지! Discord 전송 중: {html_url}")
    send_discord_message(html_url)
    save_last_release_id(release_id)
    print("[INFO] 완료.")


if __name__ == "__main__":
    main()
