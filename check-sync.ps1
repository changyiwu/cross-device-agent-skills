# 技能版本檢查／同步：比對 GDrive 原始檔 vs 四個工具的安裝副本
#
# 用法：
#   .\check-sync.ps1                  → 檢查三個技能
#   .\check-sync.ps1 startup          → 只檢查 startup
#   .\check-sync.ps1 -Sync            → 檢查後直接覆蓋四份副本，再驗證
#   .\check-sync.ps1 -NoFetch         → 跳過 git fetch（離線時用）
#
# 為什麼要先問 git 再比內容：
#   純比對「源檔 vs 副本」是相對檢查，抓不到「兩邊一起舊」——GDrive 整包還沒
#   同步完時，源檔和副本都是舊版，比對會印 OK。那種「一起降版」只有拿 origin
#   當權威才看得出來，所以 BEHIND 是硬關卡，會直接中止。
#
# 這支腳本只放在原始檔（repo 根目錄），不隨技能複製到安裝副本——
# 「檢查者」本身不能有舊版，否則檢查結果不可信。
param(
    [string[]]$Skills = @('project-init', 'startup', 'shutdown'),
    [switch]$Sync,
    [switch]$NoFetch
)

$src = $PSScriptRoot
$dests = @(
    @{ Tool = 'Claude Code'; Path = "$HOME\.claude\skills" },
    @{ Tool = 'Codex'; Path = "$HOME\.agents\skills" },
    @{ Tool = 'OpenCode'; Path = "$HOME\.config\opencode\skills" },
    @{ Tool = 'Antigravity'; Path = "$HOME\.gemini\config\skills" }
)

function Get-Snapshot($root) {
    if (-not (Test-Path $root)) { return $null }
    Get-ChildItem -Recurse -File $root | ForEach-Object {
        [pscustomobject]@{
            Path = $_.FullName.Substring($root.Length).TrimStart('\')
            Hash = (Get-FileHash $_.FullName).Hash
        }
    }
}

# ── 關卡 1：git 是版本的權威（抓「源檔與副本一起舊」）──────────────
$isRepo = $false
try {
    $null = git -C $src rev-parse --git-dir
    if ($LASTEXITCODE -eq 0) { $isRepo = $true }
}
catch {
    "WARN  找不到 git——無法偵測「源檔與副本一起舊」，以下比對只能證明兩邊一致"
}

if ($isRepo) {
    # 30 分鐘內 fetch 過就跳過（與 startup 技能同一條規則，避免多對話冗餘）
    $fetchHead = Join-Path $src '.git\FETCH_HEAD'
    $fresh = $false
    if (Test-Path $fetchHead) {
        if (((Get-Date) - (Get-Item $fetchHead).LastWriteTime).TotalMinutes -lt 30) { $fresh = $true }
    }
    if (-not $NoFetch -and -not $fresh) {
        git -C $src fetch --quiet
        if ($LASTEXITCODE -ne 0) {
            "WARN  git fetch 失敗（離線？）——無法確認源檔是否落後 origin，以下結果可能是假的 OK"
        }
    }

    $upstream = git -C $src rev-parse --abbrev-ref --symbolic-full-name '@{u}'
    if ($LASTEXITCODE -ne 0) {
        "WARN  這個分支沒有 upstream——無法確認是否落後 origin"
    }
    else {
        $behind = git -C $src rev-list --count "HEAD..$upstream"
        if ([int]$behind -gt 0) {
            "BEHIND  本機 repo 落後 $upstream $behind 個 commit"
            ""
            "→ 源檔本身就是舊的，此時比對／同步都會把舊版散布到四家。"
            "  先跑 git -C `"$src`" pull，再重跑這支腳本。"
            "  （這正是「源檔與副本一起舊」的情況：純內容比對會印 OK，只有 git 抓得到）"
            exit
        }
    }

    # worktree 有改動不一定是壞事（你自己編輯中），但必須是你認得的改動
    $dirty = git -C $src status --porcelain -- $Skills
    if ($dirty) {
        "DIRTY 技能資料夾有未 commit 的改動："
        $dirty | ForEach-Object { "        $_" }
        "      → 確認以上都是你自己改的；若有非預期的檔案，先停下來查 git（GDrive 可能餵出過期內容）"
        ""
    }
}

# ── 關卡 2：覆蓋副本（只在 -Sync 時執行）─────────────────────────
# 一律用 Copy-Item 從磁碟複製。絕不可用 Write/Edit 重建目標檔——
# 那會把 context 裡記得的舊內容寫進副本，而且事後看起來跟正常同步一樣。
if ($Sync) {
    foreach ($d in $dests) {
        if (-not (Test-Path $d.Path)) { continue }
        foreach ($s in $Skills) {
            $from = Join-Path $src $s
            if (Test-Path $from) { Copy-Item $from "$($d.Path)\" -Recurse -Force }
        }
    }
    "SYNCED 已覆蓋四份副本，以下為驗證結果："
    ""
}

# ── 關卡 3：內容比對 ──────────────────────────────────────────────
$staleCount = 0
foreach ($s in $Skills) {
    $a = Get-Snapshot (Join-Path $src $s)
    if ($null -eq $a) { "SKIP  找不到原始檔：$s"; continue }
    foreach ($d in $dests) {
        $b = Get-Snapshot (Join-Path $d.Path $s)
        if ($null -eq $b) { continue }   # 這台電腦沒裝這個工具，跳過
        $diff = Compare-Object $a $b -Property Path, Hash
        if ($diff) {
            $staleCount++
            "STALE $($d.Tool.PadRight(12)) $s"
            $diff | Group-Object Path | ForEach-Object { "        - $($_.Name)" }
        }
        else {
            "OK    $($d.Tool.PadRight(12)) $s"
        }
    }
}

""
if ($staleCount -eq 0) {
    "== 全部一致，安裝副本 == 原始檔 =="
}
else {
    "== 有 $staleCount 份安裝副本是舊版 =="
    "→ 跑 .\check-sync.ps1 -Sync 覆蓋並驗證（不要自己用 Write/Edit 重建副本）"
}
