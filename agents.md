# 跨電腦專案管理三技能（cross-device-agent-skills）（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。
> Claude Code 不讀 `agents.md`，改由 `CLAUDE.md` 的 `@agents.md` import 本檔；Claude 專屬規範寫在 `CLAUDE.md`。

## 專案簡介

維護並改進 `project-init`／`startup`／`shutdown` 三個 Agent 技能，讓專案能在**任何電腦、任何 Agent** 之間無縫接續。三個口令搞定一切：「初始化專案」「開工」「收工」。技能會自動偵測工具鏈，做到本機能達成的最高層級（L1 本地／L2 GitHub／L3 Obsidian）。

搭配內容：三師爸「AI Agent 基本功」EP06 懶人包。

## 關鍵時程

<!-- 目前無固定時程 -->

## 目標與路線圖

- [x] 階段一：三技能成形（project-init / startup / shutdown）＋ README 說明
- [x] 階段二：本專案自身完成初始化（agents.md ＋ handoff.md ＋ git ＋ Obsidian）
- [ ] 階段三：跨電腦實測（在另一台電腦「開工／收工」驗證流程；**現在也包含 macOS 實測**）
- [ ] 階段四：依實測回饋調整技能內容
- [x] 階段五：既有 30 個專案依「時效性」規則整理完畢（`agents.md` 移除 17 個 `## 最近進度`、30 個補上職責護欄；`handoff.md` 的 ⚠️ 從約 180 條分流到 33 條；缺漏的歷史先回填 Obsidian 才刪）
- [x] 階段六：跨平台改造（Windows ↔ macOS）——`platform.md` 定案（pwsh 7 唯一、路徑原則、能力分級）、`sync-skills` 與三技能改雙平台、`tools/check-platform.py` 建立可執行檢查、`file-toolkit`／`voxcpm2`／`agent-speak`／`share-report`／`clasp-gas-skill` 完成移植。**未在 macOS 實測過，那是階段三**

## 資料夾結構

```
cross-device-agent-skills/
├─ README.md                 # 技能包說明、安裝方式（同步改指向 sync-skills 技能）
├─ agents.md                 # 本檔：專案藍圖
├─ CLAUDE.md                 # 橋接檔（@agents.md，讓 Claude Code 也載得到藍圖）
├─ platform.md               # 跨平台約定（Windows ↔ macOS）：路徑原則＋四個不報錯的坑
├─ handoff.md                # 交接檔（每次收工必更新；已 gitignore，只走雲端硬碟）
├─ project-init/
│  ├─ SKILL.md               # 「初始化專案」技能
│  └─ templates/
│     ├─ agents.template.md  # 專案藍圖範本
│     ├─ claude.template.md  # CLAUDE.md 橋接檔範本
│     └─ handoff.template.md # 交接檔範本
├─ startup/SKILL.md          # 「開工」技能
├─ shutdown/SKILL.md         # 「收工」技能
├─ tools/
│  └─ check-platform.py      # 跨平台檢查器（把 platform.md 的規則變成可執行檢查，跨 repo 掃）
└─ .claude/settings.local.json
```

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md`（不進 git，只走雲端硬碟）＋`CLAUDE.md`（橋接） | 每個 session |
| L2 | GitHub | https://github.com/changyiwu/cross-device-agent-skills （公開） | 指定時 |
| L3 | Obsidian | `cross-device-agent-skills/專案工作流程.md` | 有需要時 |

## 三個檔案的職責（依「時效性」分家，不是依「詳細程度」）

| 檔案 | 時效 | 寫入方式 | 放什麼 |
|------|------|---------|--------|
| `handoff.md` | **只對下一個 session 有效**，過期即丟 | 每次收工整份重寫 | 做到哪、下一步、**這次**的暫時 workaround |
| `agents.md`（本檔） | **長期有效**，每個 session 都適用 | 只有規則本身變了才改 | 目標、路線圖、常設規則、結構 |
| Obsidian／`git log` | **歷史**：發生過什麼、為什麼 | 只增不刪 | 決策紀錄、踩坑完整版、逐次進度 |

驗收標準：**`handoff.md` 整份刪掉，不應損失任何長期資訊**——會的話代表該升級進本檔卻沒升級。

**本檔不要出現的東西**：❌ `## 最近進度`／逐次工作紀錄（本檔曾有一節，2026-08-03 移除——內容在 Obsidian「🗓️ 最近更動紀錄」條條都有）、❌ 決策理由與踩坑完整版（在 Obsidian「🧠 決策紀錄」「🕳️ 踩坑筆記」）。踩過的坑只把**結論**收斂成一條祈使句寫進下面的〈工作約定〉，原因留 Obsidian。

## 工作約定

- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- `handoff.md` **不進 git**（含真實電腦名與本機絕對路徑），已列入 `.gitignore`，跨電腦靠雲端硬碟同步——不要把它加回版控
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- **本資料夾是技能原始檔**。改動一律改這裡，改完說「同步技能」，委派全域技能 `sync-skills`（`skill-sync` 專案）覆蓋安裝副本。**同步的做法、驗證方式、注意事項都不要抄一份到本 repo**——只該有一份，在那個技能裡
- **這台電腦的技能安裝來源永遠是本機這個資料夾，不是任何遠端 repo**。README 的〈安裝〉`git clone` 是寫給外部使用者的步驟，**不要**拿來當我方的安裝／更新途徑；要更新安裝副本就從本資料夾走 `sync-skills`
- **不要把三技能的「步驟 0」加回來**（已決定不裝 chezmoi，dotfile 漂移檢查整個不做）
- 寫任何要跨 Windows／macOS 的路徑或 PowerShell 前，先讀 `platform.md`。核心一條：**路徑一律相對 cwd 或往上找，不要解析「雲端硬碟根」**（例外只有全域技能，它沒有 cwd 可當錨點）；電腦名一律 `[Environment]::MachineName`，不可用 `$env:COMPUTERNAME`（macOS 是空字串且不報錯）
- 改完跨平台相關的東西，跑 `python tools/check-platform.py` 驗一次（不帶參數＝掃所有同層專案）。**豁免有兩種**：整檔平台專屬用 repo 根目錄的 `.platform-ok`，檔案跨平台但個別行包在 `if ($IsWindows)` 裡用行內 `platform-ok:` 註解。豁免處數一定會印在總結裡——**看得見的豁免才叫豁免**
- **「一律無 BOM」有一個例外：公開懶人包裡給初學者用 `powershell.exe`（5.1）跑的 `.ps1`**。初學者的 Windows 預設沒有 pwsh 7，而 5.1 會把無 BOM 的 UTF-8 當 ANSI 讀、中文全爛。那些檔案的 BOM 是必要的，已列進各自的 `.platform-ok`，不要清
- **30 個公開 repo 的 git 歷史怎麼處理，尚未決定**：舊 commit 裡仍留著當年的 `handoff.md`。要清得重寫歷史＋強制推送 30 個 repo，屬不可逆操作。**在使用者明確決定之前，不要當成待辦逕行處理**
- 同步完的新版**要下一個 session 才生效**：技能副本是進 session 時載入的，同一個對話裡同步完仍然跑舊版。**重開 Claude Code 也算新 session**（判斷方式：比對副本 mtime 與 `Get-Process claude` 的 `StartTime`，啟動晚於寫入才是新版）
- **所有檔案一律 UTF-8 無 BOM**（`.md`／`.ps1`／`.py` 都是，沒有例外）。`SKILL.md` 帶 BOM 會讓 frontmatter 解析失敗、技能觸發不了。舊的「`.ps1` 必須含 BOM」已隨 5.1 退場而廢止，詳見 `platform.md`
- PowerShell 一律 **pwsh 7**，不支援 Windows PowerShell 5.1；跨平台能力不強求對等，mac 上沒有的能力要明說、不靜默降級（見 `platform.md`）
- **GDrive 上的 repo 一律以 git 為準，不以檔案內容或時間戳為準**。`git status` 出現 `MM` 但 `git diff HEAD` 為空時只是 LF/CRLF 差異，`git add --renormalize .` 可消除
- PowerShell 裡 `'@{u}'` **一定要用單引號包起來**，裸的 `@{` 會被當成 hashtable 語法、直接噴解析錯誤
