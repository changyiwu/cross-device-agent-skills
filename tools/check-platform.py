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
import subprocess
import sys
from pathlib import Path

# Windows 主控台預設是 cp950，會把中文輸出變亂碼並在 emoji 上直接丟 UnicodeEncodeError。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---- 逐行的文字規則 -------------------------------------------------------
# 分隔符一律寫 [\\/]+ 而不是 [\\/]：JSON 與部分程式語言的字串會把反斜線跳脫成兩個，
# 只允許一個分隔符的話，.mcp.json 那種跳脫過的 Windows 路徑會整批逃過檢查（實測踩過）。
LINE_RULES = [
    (re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+\S"), "寫死本機使用者絕對路徑"),
    (re.compile(r"[A-Za-z]:[\\/]+我的雲端硬碟"), "寫死雲端硬碟絕對路徑"),
    (re.compile(r"\.venv[\\/]+(Scripts|bin)[\\/]+"), "寫死 venv 路徑（Scripts / bin 兩平台不同）"),
    # 上一條只抓得到「.venv 緊接其下一層」的字面。實測 voxcpm2 與 file-toolkit 都是把
    # venv 根目錄放進變數、再接下一層的直譯器路徑，整個逃過檢查——所以要獨立抓後半段。
    (re.compile(r"[\\/'\"]+(Scripts)[\\/]+(python|pip)"), "寫死直譯器子目錄（mac 是 bin/python）"),
    (re.compile(r"\$env:COMPUTERNAM[E]"), "用了 COMPUTERNAME（macOS 是空字串且不報錯）"),
    (re.compile(r"\$env:(LOCALAPPDATA|APPDATA|USERPROFILE|PROGRAMFILES|PROGRAMDATA|SYSTEMROOT)"),
     "用了 Windows 專屬環境變數（macOS 是 $null，Join-Path 會組出錯的路徑）"),
    # 上面幾條都要求路徑開頭有磁碟機代號，所以「變數 ＋ 反斜線」這種組法整個看不見。
    # 這是最會咬人的一類：在 macOS 上反斜線是合法檔名字元，不是分隔符，於是
    # HOME 變數接反斜線會組出一個「名字裡有反斜線」的單層路徑，Test-Path 靜默回 False，
    # 技能只會說「找不到腳本」——又是一個不報錯的失敗。實測 7 個 repo 中鏢。
    #
    # 判別「路徑」與「正則跳脫」：反斜線後面要接兩個路徑字元（第一個可以是點，
    # 因為 .claude 這類隱藏目錄很常見）。正則裡的跳脫幾乎都是單字元類別，
    # 後面接的是引號、星號或大括號，所以自然被排除。已知的代價是
    # 「反斜線後面緊接角括號佔位符」那種寫法抓不到（保守漏報，不是誤報）。
    (re.compile(r"\$[A-Za-z_][A-Za-z0-9_:]*\\[\w.]\w"),
     "用反斜線組路徑（macOS 的分隔符是斜線，反斜線會變成檔名的一部分）"),
]

# .bat / .cmd 刻意不掃：cmd.exe 只有 Windows 有，那種檔案**整個就是 Windows 專屬**，
# 在裡面挑「Windows 路徑」是定義上的誤報。macOS 的對應做法是別的入口，不是改那個檔。
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".psm1", ".yaml", ".yml", ".txt",
                 ".json", ".js", ".mjs", ".sh", ".toml"}

# 整份都是程式碼，逐行都檢查。
CODE_SUFFIXES = {".py", ".ps1", ".psm1", ".sh", ".js", ".mjs",
                 ".json", ".yaml", ".yml", ".toml"}

FENCE = re.compile(r"^\s*(```|~~~)")
# 圍籬的語言標記。上面那條只判「是不是圍籬」，這條另外把語言抓出來，
# 給下面「只在 PowerShell 語境成立」的規則用。
FENCE_LANG = re.compile(r"^\s*(?:```|~~~)\s*([A-Za-z0-9_+-]*)")
PS_LANGS = {"powershell", "pwsh", "ps1", "ps"}

# ---- 只在 PowerShell 語境成立的規則 ---------------------------------------
# 為什麼要分語境：**兩種語言對反斜線的語意相反**。PowerShell 的跳脫字元是反引號，
# 所以字串裡的反斜線幾乎必然是路徑分隔符；Python 剛好相反（跳脫與正則滿天飛）。
# 混在一起掃必然誤報——實測「任何語言都掃」的版本會把 re.split(r"\r?\n\r?\n") 與
# JSON 裡的 "2 天前是\n4×(-2)" 全算成路徑。
#
# 上面那條 LINE_RULES 的路徑規則都要求開頭有磁碟機代號或 `$變數`，所以
# 'skills\clasp-setup' 這種「整串都是字面、前面沒有變數」的寫法完全不在視野內。
# 2026-09-20 補這條時一次掃出 12 個 repo；在那之前它讓 youtube-publish-kit 的
# SKILL.md 在只修好一半的狀態下顯示 0 命中。
PS_LINE_RULES = [
    (re.compile(r"\\[\w.][\w.-]"),
     "用反斜線組路徑（macOS 的分隔符是斜線，反斜線會變成檔名的一部分）"),
]
# PowerShell 裡唯一會把反斜線當正則用的場合：字串被餵給這些運算子／型別。
PS_REGEX_OPS = re.compile(
    r"-(?:c|i)?(?:not)?(?:match|replace|split)\b|\[regex\]|Select-String|"
    r"RegularExpressions", re.I)
# 補上一條：正則被存進變數或陣列時，運算子不在同一行。字元類別與量詞是它的指紋。
# 實測只濾掉 2 行（rdq-skill 的 'references/[A-Za-z0-9._/-]+\.md' 與 sync-skills
# 的 $skip），沒有誤殺任何真命中。
PS_REGEX_SHAPE = re.compile(r"\[[^\]\n]{3,}\]|\{\d+(?:,\d*)?\}")

# 行內豁免：這一行的平台專屬寫法是刻意的（最常見是「已經包在 if ($IsWindows) 裡」，
# 而逐行規則看不到那層 guard）。用行內標記而不是整檔豁免，才不會連同一個檔案裡
# 未來新增的真問題一起蓋掉。寫法：在該行加註解 `platform-ok: <理由>`。
INLINE_OK = re.compile(r"platform-ok")

# 區塊豁免：教學文件常寫成「Windows 一塊、macOS 一塊」，Windows 那塊的平台專屬寫法
# 是刻意的。這種情形**不可以**要求作者在程式碼裡加行內 `platform-ok` 註解——那些區塊是
# 給初學者整段複製貼上的，註解會被一起貼走，等於拿文件品質換 lint 乾淨。
HEADING = re.compile(r"^#{1,6}\s")
# 標題形式實測有 `**Windows（PowerShell）**`、`### Windows PowerShell`、`Windows 使用 PowerShell：`
# 等十幾種，所以前綴一律放行，只要求該行以 Windows 起頭。
WINDOWS_LABEL = re.compile(r"^[\s>*#\-\d.、|]*\**\s*Windows\b", re.I)
MAC_LABEL = re.compile(r"\b(macOS|Mac OS|Linux)\b", re.I)
# 上面那條是「這一節有沒有提到 mac」的全行搜尋；這條是「這個區塊標題是不是 mac」。
MACOS_LABEL = re.compile(r"^[\s>*#\-\d.、|]*\**\s*(macOS|Mac OS|Linux)\b", re.I)


def md_paired_platform_lines(lines):
    """算出「已經配好對的平台區塊」佔哪些行（1-based）。

    **豁免條件不是「標了平台」，而是「標了平台且同一節裡兩個平台都在」。**
    這條分野是本函式的全部重點：只看標題就豁免的話，會把「Windows 專屬、mac 版根本
    還沒寫」的區塊一併藏掉——那正是這支工具要找出來的東西，藏掉等於讓工具說謊。

    兩邊都要豁免，不是只豁免 Windows：macOS 區塊寫 venv 底下 bin 那層的直譯器是正確的，
    但那同樣會命中「venv 路徑」規則。只放行一邊的話，補 mac 版反而製造新的誤報
    （實測就是這樣發現的）。

    節以 Markdown 標題切開；整份沒有標題就算一節。
    """
    section = 0
    in_fence = False
    sec_of_line = []
    mac_sections, win_sections = set(), set()
    for line in lines:
        if not in_fence and HEADING.match(line):
            section += 1
        sec_of_line.append(section)
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if MAC_LABEL.search(line):
            mac_sections.add(section)
        if WINDOWS_LABEL.match(line):
            win_sections.add(section)
    paired_sections = mac_sections & win_sections

    paired = set()
    in_fence = False
    start = 0
    for i, line in enumerate(lines):
        if not FENCE.match(line):
            continue
        if not in_fence:
            in_fence, start = True, i
            continue
        in_fence = False
        label = next((lines[j] for j in range(start - 1, -1, -1) if lines[j].strip()), "")
        labelled = WINDOWS_LABEL.match(label) or MACOS_LABEL.match(label)
        if labelled and sec_of_line[start] in paired_sections:
            paired.update(range(start + 2, i + 1))   # 圍籬內的行，換算成 1-based
    return paired


def code_lines(path: Path, text: str):
    """產生 (行號, 內容)，但只給「會被執行的行」。

    這是本工具最重要的一條設計：**散文不檢查，只檢查程式碼**。
    否則「⚠️ 不可用某某環境變數」這類**禁止**該寫法的警告句會自己命中，
    教學文件裡刻意寫給讀者看的 Windows 路徑也會全部中——實測第一版 107 筆命中
    有一大半是這兩類。誤報會訓練人忽略警告，那比沒有檢查更危險。

    附帶一提：連這段說明都不能寫出被禁的字面，否則本檔自己就會命中。

    .md 只看 ``` 圍籬內的內容；程式碼檔整份都看。

    第三個回傳值是「這一行落在已配對的 Windows 區塊裡」，交給呼叫端決定要不要靜音。
    第四個是「這一行是不是 PowerShell」，給 PS_LINE_RULES 用——.md 靠圍籬的語言標記，
    程式碼檔靠副檔名。標記不寫語言的圍籬一律不算 PowerShell（寧可漏，不要誤報）。
    """
    lines = text.splitlines()
    suffix = path.suffix.lower()
    if suffix in CODE_SUFFIXES:
        is_ps = suffix in {".ps1", ".psm1"}
        for lineno, line in enumerate(lines, start=1):
            yield lineno, line, False, is_ps
        return

    paired = md_paired_platform_lines(lines)
    inside = False
    lang = ""
    for lineno, line in enumerate(lines, start=1):
        if FENCE.match(line):
            if not inside:
                m = FENCE_LANG.match(line)
                lang = (m.group(1) or "").lower() if m else ""
            else:
                lang = ""
            inside = not inside
            continue
        if inside:
            yield lineno, line, lineno in paired, lang in PS_LANGS

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "site-packages", "__pycache__",
             "dist", "build", "generated", "outputs", "output", "tmp", "scratch",
             ".skill-install", ".netlify", "待刪除"}   # .netlify 是部署工具產生的本機狀態

SKIP_NAMES = {"package-lock.json", "poetry.lock"}


def read_allowlist(root: Path):
    """讀 repo 根目錄的 .platform-ok：列出「刻意保留平台專屬寫法」的檔案。

    兩種典型：教學文件裡示範 Windows 指令、旁邊已註明 macOS 版本的那種；
    以及**目標讀者是 Windows PowerShell 5.1 的公開教學腳本**——那些檔案的 BOM 是
    必要的（5.1 把無 BOM 的 UTF-8 當 ANSI 讀，中文會爛掉、腳本 parse 失敗），
    不是還沒清掉的遺毒。

    列在這裡的檔案**整份跳過**，含 BOM 檢查。**跳掉幾處會印在總結裡**——
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


def tracked_files(root: Path):
    """回傳 git 追蹤中的檔案集合；不是 repo 或 git 不可用時回傳 None（＝全掃）。

    依專案通則「GDrive 上的 repo 一律以 git 為準」：git 不追蹤的檔案不屬於這個 repo，
    自然也不會是這個 repo 的跨平台缺陷。實測擋掉的正是 file-toolkit/_work 的拋棄式
    檢查腳本，以及 .mcp.json／settings.local.json 這類本機專屬設定。

    代價要講明白：**還沒 commit 的新檔案也會一起被跳過**，所以跳過幾個檔案要印在總結裡。
    """
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                             capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return {q for q in out.stdout.decode("utf-8", errors="replace").split("\0") if q}


def scan_repo(root: Path):
    """回傳 (findings, notes, files_allowed, muted, untracked)。findings 是 (相對路徑, 行號, 標籤)。"""
    findings, notes = [], []
    allow = read_allowlist(root)
    tracked = tracked_files(root)
    files_allowed = muted = untracked = 0

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

        if tracked is not None and rel.as_posix() not in tracked:
            untracked += 1
            continue

        if rel.as_posix() in allow:
            files_allowed += 1
            continue

        raw = path.read_bytes()
        if raw[:3] == b"\xef\xbb\xbf":
            findings.append((rel, 1, "檔案有 BOM（規則是一律無 BOM）"))

        text = raw.decode("utf-8", errors="replace")
        for lineno, line, in_paired_block, is_ps in code_lines(path, text):
            # 先確定這行真的會命中才算「靜音一處」——否則一個十行的 Windows 區塊會被記成
            # 豁免十處，把數字灌水。豁免要看得見，但也要是真的數字。
            silent = in_paired_block or bool(INLINE_OK.search(line))
            hit_here = False
            for pattern, label in LINE_RULES:
                if pattern.search(line):
                    hit_here = True
                    if silent:
                        muted += 1
                    else:
                        findings.append((rel, lineno, label))

            # PowerShell 專屬規則。已經被上面抓到的行就不再報一次——那條路徑規則
            # 是這條的子集（`$變數\檔名` 一定也是「反斜線接路徑字元」），同一行報兩次
            # 只是把數字灌水，對修的人沒有多給任何資訊。
            if not is_ps or hit_here:
                continue
            if PS_REGEX_OPS.search(line) or PS_REGEX_SHAPE.search(line):
                continue
            for pattern, label in PS_LINE_RULES:
                if pattern.search(line):
                    if silent:
                        muted += 1
                    else:
                        findings.append((rel, lineno, label))

    return findings, notes, files_allowed, muted, untracked


def main(argv):
    if argv:
        targets = [Path(a).resolve() for a in argv]
    else:
        # 預設：本 repo 的上一層底下所有 git 專案
        parent = Path(__file__).resolve().parent.parent.parent
        targets = sorted(p for p in parent.iterdir() if p.is_dir() and (p / ".git").exists())

    total = 0
    sum_allowed = sum_muted = sum_untracked = 0
    by_label = {}
    clean = []

    for root in targets:
        if not root.is_dir():
            print(f"⚠️ 找不到：{root}")
            continue
        findings, notes, files_allowed, muted, untracked = scan_repo(root)
        sum_allowed += files_allowed
        sum_muted += muted
        sum_untracked += untracked
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
    # 三種豁免的單位不同（檔案／命中／檔案），混成一個數字就看不出被蓋掉的是什麼，分開報。
    if sum_allowed:
        print(f"\n🔇 整檔豁免 {sum_allowed} 個檔案（.platform-ok）")
    if sum_muted:
        print(f"🔇 靜音 {sum_muted} 處命中（platform-ok 行內標記 ＋ 已配對的平台區塊）")
    if sum_untracked:
        print(f"🔇 跳過 {sum_untracked} 個未進版控的檔案（git ls-files 之外）")
    if clean:
        print(f"\n✅ 乾淨（{len(clean)}）：{'、'.join(clean)}")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
