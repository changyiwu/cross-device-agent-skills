#!/usr/bin/env python3
"""跨平台檢查器：把 platform.md 的規則變成可執行的檢查。

用法：
    python tools/check-platform.py                # 掃本 repo 的所有同層專案
    python tools/check-platform.py <路徑> [路徑…]  # 只掃指定的專案

跟 yaml-infographic/tools/validate_repo.py 的差別：**這支不會遇到第一個命中就停**。
它要產出的是完整工作清單，不是守門。第一次跑出來的東西就是待辦清單。

規則的寫法必須讓「這個檔案自己」不會命中——例如環境變數那條用 [E] 把字面拆開，
路徑那幾條靠「一定要有磁碟機代號開頭」自然避開。改規則時先確認這點還成立。
"""

import re
import sys
from pathlib import Path

# Windows 主控台預設是 cp950，會把中文輸出變亂碼並在 emoji 上直接丟 UnicodeEncodeError。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---- 逐行的文字規則 -------------------------------------------------------
LINE_RULES = [
    (re.compile(r"[A-Za-z]:[\\/]Users[\\/]\S"), "寫死本機使用者絕對路徑"),
    (re.compile(r"[A-Za-z]:[\\/]我的雲端硬碟"), "寫死雲端硬碟絕對路徑"),
    (re.compile(r"\.venv[\\/](Scripts|bin)[\\/]"), "寫死 venv 路徑（Scripts / bin 兩平台不同）"),
    # 上一條只抓得到「.venv 緊接其下一層」的字面。實測 voxcpm2 與 file-toolkit 都是把
    # venv 根目錄放進變數、再接下一層的直譯器路徑，整個逃過檢查——所以要獨立抓後半段。
    (re.compile(r"[\\/'\"](Scripts)[\\/](python|pip)"), "寫死 Scripts\\python（mac 是 bin/python）"),
    (re.compile(r"\$env:COMPUTERNAM[E]"), "用了 COMPUTERNAME（macOS 是空字串且不報錯）"),
    (re.compile(r"\$env:(LOCALAPPDATA|APPDATA|USERPROFILE|PROGRAMFILES|PROGRAMDATA|SYSTEMROOT)"),
     "用了 Windows 專屬環境變數（macOS 是 $null，Join-Path 會組出錯的路徑）"),
]

# .bat / .cmd 刻意不掃：cmd.exe 只有 Windows 有，那種檔案**整個就是 Windows 專屬**，
# 在裡面挑「Windows 路徑」是定義上的誤報。macOS 的對應做法是別的入口，不是改那個檔。
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".psm1", ".yaml", ".yml", ".txt",
                 ".json", ".js", ".mjs", ".sh", ".toml"}

# 整份都是程式碼，逐行都檢查。
CODE_SUFFIXES = {".py", ".ps1", ".psm1", ".sh", ".js", ".mjs",
                 ".json", ".yaml", ".yml", ".toml"}

FENCE = re.compile(r"^\s*(```|~~~)")

# 行內豁免：這一行的平台專屬寫法是刻意的（最常見是「已經包在 if ($IsWindows) 裡」，
# 而逐行規則看不到那層 guard）。用行內標記而不是整檔豁免，才不會連同一個檔案裡
# 未來新增的真問題一起蓋掉。寫法：在該行加註解 `platform-ok: <理由>`。
INLINE_OK = re.compile(r"platform-ok")


def code_lines(path: Path, text: str):
    """產生 (行號, 內容)，但只給「會被執行的行」。

    這是本工具最重要的一條設計：**散文不檢查，只檢查程式碼**。
    否則「⚠️ 不可用某某環境變數」這類**禁止**該寫法的警告句會自己命中，
    教學文件裡刻意寫給讀者看的 Windows 路徑也會全部中——實測第一版 107 筆命中
    有一大半是這兩類。誤報會訓練人忽略警告，那比沒有檢查更危險。

    附帶一提：連這段說明都不能寫出被禁的字面，否則本檔自己就會命中。

    .md 只看 ``` 圍籬內的內容；程式碼檔整份都看。
    """
    if path.suffix.lower() in CODE_SUFFIXES:
        yield from enumerate(text.splitlines(), start=1)
        return

    inside = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            inside = not inside
            continue
        if inside:
            yield lineno, line

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "site-packages", "__pycache__",
             "dist", "build", "generated", "outputs", "output", "tmp", "scratch",
             ".skill-install", "待刪除"}

SKIP_NAMES = {"package-lock.json", "poetry.lock"}


def read_allowlist(root: Path):
    """讀 repo 根目錄的 .platform-ok：列出「刻意保留平台專屬寫法」的檔案。

    典型是教學文件裡示範 Windows 指令、旁邊已註明 macOS 版本的那種。
    這些檔案跳過逐行規則（BOM 仍然檢查），而且**跳掉幾個檔會印在總結裡**——
    豁免必須看得見，否則就變成偷偷關掉檢查。
    """
    f = root / ".platform-ok"
    if not f.is_file():
        return set()
    entries = set()
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            entries.add(line.replace("\\", "/"))
    return entries


def scan_repo(root: Path):
    """回傳 (findings, notes, skipped)。findings 是 (相對路徑, 行號, 標籤)。"""
    findings, notes = [], []
    allow = read_allowlist(root)
    skipped = 0

    if (root / ".git").exists() and not (root / ".gitattributes").is_file():
        notes.append("缺 .gitattributes（換行約定沒定，autocrlf 的漏洞是開著的）")

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if SKIP_DIRS.intersection(rel.parts) or path.name in SKIP_NAMES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        raw = path.read_bytes()
        if raw[:3] == b"\xef\xbb\xbf":
            findings.append((rel, 1, "檔案有 BOM（規則是一律無 BOM）"))

        if rel.as_posix() in allow:
            skipped += 1
            continue

        text = raw.decode("utf-8", errors="replace")
        for lineno, line in code_lines(path, text):
            if INLINE_OK.search(line):
                skipped += 1
                continue
            for pattern, label in LINE_RULES:
                if pattern.search(line):
                    findings.append((rel, lineno, label))

    return findings, notes, skipped


def main(argv):
    if argv:
        targets = [Path(a).resolve() for a in argv]
    else:
        # 預設：本 repo 的上一層底下所有 git 專案
        parent = Path(__file__).resolve().parent.parent.parent
        targets = sorted(p for p in parent.iterdir() if p.is_dir() and (p / ".git").exists())

    total = 0
    total_skipped = 0
    by_label = {}
    clean = []

    for root in targets:
        if not root.is_dir():
            print(f"⚠️ 找不到：{root}")
            continue
        findings, notes, skipped = scan_repo(root)
        total_skipped += skipped
        if not findings and not notes:
            clean.append(root.name)
            continue

        print(f"\n=== {root.name} ===")
        for note in notes:
            print(f"  ⚠️ {note}")
        for rel, lineno, label in findings:
            print(f"  {rel}:{lineno}  {label}")
            by_label[label] = by_label.get(label, 0) + 1
        total += len(findings)

    print("\n" + "=" * 60)
    print(f"掃描 {len(targets)} 個專案，命中 {total} 處")
    for label, count in sorted(by_label.items(), key=lambda kv: -kv[1]):
        print(f"  {count:4}  {label}")
    if total_skipped:
        print(f"\n🔇 豁免 {total_skipped} 處（.platform-ok 檔案 ＋ platform-ok 行內標記）")
    if clean:
        print(f"\n✅ 乾淨（{len(clean)}）：{'、'.join(clean)}")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
