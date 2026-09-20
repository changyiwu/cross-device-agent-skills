# 跨電腦專案管理三技能（cross-device-agent-skills）（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。
> Claude Code 自 v2.1.277 起可原生讀 `AGENTS.md`，但**有 `CLAUDE.md` 時就只讀 `CLAUDE.md`**（預設 `claude-md-or-agents-md`），所以本專案一律保留 `CLAUDE.md` 的 `@AGENTS.md` import；Claude 專屬規範寫在 `CLAUDE.md`。

## 專案簡介

維護並改進 `project-init`／`startup`／`shutdown` 三個 Agent 技能，讓專案能在**任何電腦、任何 Agent** 之間無縫接續。三個口令搞定一切：「初始化專案」「開工」「收工」。技能會自動偵測工具鏈，做到本機能達成的最高層級（L1 本地／L2 GitHub／L3 Obsidian）。

## 關鍵時程

<!-- 目前無固定時程 -->

## 目標與路線圖

- [x] 階段一：三技能成形（project-init / startup / shutdown）＋ README 說明
- [x] 階段二：本專案自身完成初始化（AGENTS.md ＋ handoff.md ＋ git ＋ Obsidian）
- [ ] 階段三：跨電腦實測（在另一台電腦「開工／收工」驗證流程；**現在也包含 macOS 實測**）
- [ ] 階段四：依實測回饋調整技能內容
- [x] 階段五：既有 30 個專案依「時效性」規則整理完畢（`AGENTS.md` 移除 17 個 `## 最近進度`、30 個補上職責護欄；`handoff.md` 的 ⚠️ 從約 180 條分流到 33 條；缺漏的歷史先回填 Obsidian 才刪）
- [x] 階段七：全 `agents/` 移除原作者頻道品牌署名（8 個 repo 已改）——`LICENSE`／`LICENSE-ASSETS.md` 與各 repo 一句原作者歸屬保留，`sensebar-agent-knowledge-vault-builder` 整個 repo 例外不動
- [x] 階段六：跨平台改造（Windows ↔ macOS）——`platform.md` 定案（pwsh 7 唯一、路徑原則、能力分級）、`sync-skills` 與三技能改雙平台、`tools/check-platform.py` 建立可執行檢查、`file-toolkit`／`voxcpm2`／`agent-speak`／`share-report`／`clasp-gas-skill` 完成移植。**未在 macOS 實測過，那是階段三**
- [x] 階段八：藍圖檔名統一為大寫 `AGENTS.md`（36 個 repo 改名、384 處引用更新，3 個原本就是大寫）——Claude Code v2.1.277 起原生支援 `AGENTS.md`，但經評估**保留 `CLAUDE.md` 橋接檔**，理由見〈工作約定〉

## 資料夾結構

```
cross-device-agent-skills/
├─ README.md                 # 技能包說明、安裝方式（同步改指向 sync-skills 技能）
├─ AGENTS.md                 # 本檔：專案藍圖
├─ CLAUDE.md                 # 橋接檔（@AGENTS.md，讓 Claude Code 也載得到藍圖）
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
| L1 | 本地（GDrive） | `AGENTS.md`＋`handoff.md`（不進 git，只走雲端硬碟）＋`CLAUDE.md`（橋接） | 每個 session |
| L2 | GitHub | https://github.com/changyiwu/cross-device-agent-skills （公開） | 指定時 |
| L3 | Obsidian | `cross-device-agent-skills/專案工作流程.md` | 有需要時 |

## 三個檔案的職責（依「時效性」分家，不是依「詳細程度」）

| 檔案 | 時效 | 寫入方式 | 放什麼 |
|------|------|---------|--------|
| `handoff.md` | **只對下一個 session 有效**，過期即丟 | 每次收工整份重寫 | 做到哪、下一步、**這次**的暫時 workaround |
| `AGENTS.md`（本檔） | **長期有效**，每個 session 都適用 | 只有規則本身變了才改 | 目標、路線圖、常設規則、結構 |
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
- **`.mcp.json` 是本機專屬、已 gitignore，不要加回版控**。換到別台電腦（含 mac）要自己寫一份，不可直接沿用 Windows 這份
- **不要把三技能的「步驟 0」加回來**（已決定不裝 chezmoi，dotfile 漂移檢查整個不做）
- 寫任何要跨 Windows／macOS 的路徑或 PowerShell 前，先讀 `platform.md`。核心一條：**路徑一律相對 cwd 或往上找，不要解析「雲端硬碟根」**（例外只有全域技能，它沒有 cwd 可當錨點）；電腦名一律 `[Environment]::MachineName`，不可用 `$env:COMPUTERNAME`（macOS 是空字串且不報錯）
- 改完跨平台相關的東西，跑 `python tools/check-platform.py` 驗一次（不帶參數＝掃所有同層專案）。**只掃 git 追蹤中的檔案**——本機專屬的 `_work/`、`.mcp.json`、`settings.local.json` 因此自動排除，代價是還沒 commit 的新檔也掃不到。**豁免有三種**：①整檔平台專屬用 repo 根目錄的 `.platform-ok`；②檔案跨平台但個別行包在 `if ($IsWindows)` 裡，用行內 `platform-ok:` 註解；③教學文件裡標了平台的程式碼區塊，**同一節裡 Windows 與 macOS 兩邊都在**時自動靜音，兩邊對稱（只放行 Windows 的話，補出來的 macOS 版寫 `.venv/bin/python` 反而製造新誤報）。不可用行內註解代替——那些區塊是給初學者整段複製貼上的，註解會被一起貼走。三種豁免的數量分開印在總結裡——**看得見的豁免才叫豁免**
- 自動靜音**只認明確標了平台的區塊**。文件裡「Windows 版在上、macOS 版在下但上面那塊沒標題」的寫法仍會命中，該補的是標題（例如 `**Windows（PowerShell）**`），不是去放寬工具。標題要**自成一行**——圍籬前最近的非空行若是說明的續行，就配不到對
- **「一律無 BOM」有一個例外：公開懶人包裡給初學者用 `powershell.exe`（5.1）跑的 `.ps1`**。初學者的 Windows 預設沒有 pwsh 7，而 5.1 會把無 BOM 的 UTF-8 當 ANSI 讀、中文全爛。那些檔案的 BOM 是必要的，已列進各自的 `.platform-ok`，不要清
- **30 個公開 repo 的 git 歷史怎麼處理，尚未決定**：舊 commit 裡仍留著當年的 `handoff.md`。要清得重寫歷史＋強制推送 30 個 repo，屬不可逆操作。**在使用者明確決定之前，不要當成待辦逕行處理**
- 同步完的新版**要下一個 session 才生效**：技能副本是進 session 時載入的，同一個對話裡同步完仍然跑舊版。**重開 Claude Code 也算新 session**（判斷方式：比對副本 mtime 與 `Get-Process claude` 的 `StartTime`，啟動晚於寫入才是新版）
- **所有檔案一律 UTF-8 無 BOM**（`.md`／`.ps1`／`.py` 都是，沒有例外）。`SKILL.md` 帶 BOM 會讓 frontmatter 解析失敗、技能觸發不了。舊的「`.ps1` 必須含 BOM」已隨 5.1 退場而廢止，詳見 `platform.md`
- PowerShell 一律 **pwsh 7**，不支援 Windows PowerShell 5.1；跨平台能力不強求對等，mac 上沒有的能力要明說、不靜默降級（見 `platform.md`）
- **GDrive 上的 repo 一律以 git 為準，不以檔案內容或時間戳為準**。`git status` 出現 `MM` 但 `git diff HEAD` 為空時只是 LF/CRLF 差異，`git add --renormalize .` 可消除
- **原作者的頻道品牌不要加回來**。2026-08-22 依使用者決定，全 `agents/` 移除「三師爸 Sense Bar」「@sensebar」等頻道推廣署名、YouTube 連結與影片集數綁定（本 repo 的 README 也不再自稱「EP06 懶人包」）。保留的只有兩種：各 repo `LICENSE`／`LICENSE-ASSETS.md` 的原始著作權行（MIT 保留義務，**永遠不可刪**），以及出處說明裡「原作者三師爸（`mathruffian-dot`）、本專案為改作版本」一句。`mathruffian-dot` 的上游 URL 一律保留——那是安裝指令與出處追溯要用的。例外：`sensebar-agent-knowledge-vault-builder` 整個 repo 不動，它的存在目的就是抓該頻道字幕。
- PowerShell 裡 `'@{u}'` **一定要用單引號包起來**，裸的 `@{` 會被當成 hashtable 語法、直接噴解析錯誤
- **跨 Agent 藍圖的檔名一律是大寫 `AGENTS.md`**（開放標準的正式拼法，也是 Claude Code 原生辨識的拼法）。2026-09-20 全 `agents/` 36 個 repo 由舊的小寫 `agents.md` 統一改名。Windows 與 macOS 的檔案系統大小寫不敏感，**在這兩台永遠測不出檔名拼錯**，所以命名靠約定顧、不要靠實測；改名一律 `git mv -f`（`core.ignorecase=true` 時不加 `-f` git 看不到改名）
- **`CLAUDE.md` 橋接檔不要刪**。Claude Code 已能原生讀 `AGENTS.md`，但那是**二選一**不是兩份都讀：有 `CLAUDE.md` 就完全不碰 `AGENTS.md`。留著 import 不會讀兩次，且有四種場合原生讀不到（Amazon Bedrock、telemetry 停用、`disableAllHooks`／`allowManagedHooksOnly`、安裝或升級後的第一個 session）——跨電腦跨 Agent 正是本專案的承諾，不能賭。各專案的 `CLAUDE.md` 除了 import 還放著 Claude 專屬規範，更不能刪
- 驗證橋接生效的方式**依載入途徑而不同**：走 `@AGENTS.md` import 就看 `/context` 的 **Memory files** 有沒有列到 `CLAUDE.md`；若哪天改走原生讀取，`AGENTS.md` **不會**出現在 `/memory` 與 `/context` 的清單裡，要改看 session 開頭的 `AGENTS.md loaded:` 那行——用錯方式會得到假陰性
