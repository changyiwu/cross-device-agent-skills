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
- [ ] 階段三：跨電腦實測（在另一台電腦「開工／收工」驗證流程）
- [ ] 階段四：依實測回饋調整技能內容

## 資料夾結構

```
cross-device-agent-skills/
├─ README.md                 # 技能包說明、安裝方式、四工具同步指令
├─ agents.md                 # 本檔：專案藍圖
├─ CLAUDE.md                 # 橋接檔（@agents.md，讓 Claude Code 也載得到藍圖）
├─ handoff.md                # 交接檔（每次收工必更新）
├─ project-init/
│  ├─ SKILL.md               # 「初始化專案」技能
│  └─ templates/
│     ├─ agents.template.md  # 專案藍圖範本
│     ├─ claude.template.md  # CLAUDE.md 橋接檔範本
│     └─ handoff.template.md # 交接檔範本
├─ startup/SKILL.md          # 「開工」技能
├─ shutdown/SKILL.md         # 「收工」技能
└─ .claude/settings.local.json
```

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md`＋`CLAUDE.md`（橋接） | 每個 session |
| L2 | GitHub | https://github.com/changyiwu/cross-device-agent-skills （公開） | 指定時 |
| L3 | Obsidian | `cross-device-agent-skills/專案工作流程.md` | 有需要時 |

## 工作約定

- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- **本資料夾是技能原始檔**。改動一律改這裡，改完說「同步技能」，委派全域技能 `sync-skills`（`skill-sync` 專案）覆蓋安裝副本。**同步的做法、驗證方式、注意事項都不要抄一份到本 repo**——只該有一份，在那個技能裡
- 編輯 `SKILL.md` 時不可存成含 BOM 的 UTF-8，否則 frontmatter 解析失敗、技能觸發不了
- `.ps1` 規則相反：**必須含 BOM**，否則 PowerShell 5.1 當成 ANSI 讀，中文字串爛掉

## 最近進度

- 2026-07-22：將 Codex 全域 Skill 安裝位置更新為 `~/.agents/skills/`，並同步 README、project-init、startup、shutdown 四處說明。
- 2026-07-22（晚）：`project-init` 建 GitHub repo 時改為**詢問使用者公開或私有**（原本寫死 private），並同步四份安裝副本。
- 2026-07-26：新增「同步安裝副本前先跑 `git diff HEAD --stat`」的防呆（README ＋ `shutdown/SKILL.md` 兩處）。起因是本次 GDrive 餵出過期檔案內容，據此同步一度把四份副本降版。已確認 Codex 讀取路徑 `~/.agents/skills/` 正確。
- 2026-07-27（NB-YI）：發現這台電腦四份副本的 `shutdown` 都停在 a53bb0f 之前（`startup`／`project-init` 正常），先補同步。接著新增 `check-sync.ps1` 並在三個技能加「步驟 0」前置檢查——原本只有 `shutdown` 在「收工的專案是技能 repo 本身」時才比對版本，在其他專案跑三技能完全不檢查。腳本含三道關卡，其中 `BEHIND` 是硬關卡（連 `-Sync` 也擋），用來補「源檔與副本一起舊」的偵測盲區：那種情況純內容比對會印**假的 `OK`**。四項關卡行為均實測驗證過。（`check-sync.ps1` 已於 07-29 移除，見下）
- 2026-07-28（33fc992）：`project-init` 補建 `CLAUDE.md` 橋接檔（Claude Code 不讀 `agents.md`），新增 `templates/claude.template.md`，README ＋ agents.md 同步說明。
- 2026-07-29（aaf273d）：移除 `check-sync.ps1`，三技能步驟 0 改用 `chezmoi status`——版本檢查的職責交給 dotfile 管理工具，技能只負責回報、不自己決定 `apply`／`add`。代價是步驟 0 目前只涵蓋已納入 chezmoi 的檔案，故新增階段五。
- 2026-07-29（a516780，NB-YI）：刪掉 `shutdown/SKILL.md` 的「收工的專案是技能 repo 本身時」整節，步驟 0 底下指向它的那句改為指向 README 的「本副本的設定（changyiwu）」同步段。收工流程自此**不再內含執行同步的環節**，同步一律手動跑 README 那段 `Copy-Item`。
- 2026-07-29（NB-YI，晚）：三技能步驟 0 從自己跑 `chezmoi status` 改為**委派 `chezmoi-sync` 技能**（`chezmoi-setup` 專案）跑到它的「步驟 2」為止，有落差才升級成它的完整流程。起因：`chezmoi status` 只比 source ↔ target，兩邊一起舊會印**假的乾淨**，要補得再問 git「來源 repo vs GitHub」——而那套判讀（含先收後拉的順序、`readonly_` 前綴、憑證檢查）`chezmoi-sync` 已經寫得更完整，不該在三技能裡再抄一份。同時放寬 `startup` 核心原則 #1：dotfile 的處置委派出去，不算違反開工唯讀。README 的〈步驟 0〉整節同步改寫。**尚未生效**：三台都還沒裝 chezmoi（遠端 repo `dotfiles-agent-skills` 已刪待重建），且 `chezmoi-sync` 還沒安裝到任何技能目錄，故目前每次都走「未安裝 → 略過」。本次在 **PC-YI-SL** 收工，四份副本已在這台同步（hash 全對）；**NB-YI 的四份副本尚未跟上**。
