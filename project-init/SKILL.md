---
name: project-init
description: 專案初始化技能（三層級自動偵測）。當使用者說「初始化專案」、「專案初始化」、「幫這個專案做初始化」、「開新專案」、「建立專案藍圖」、「幫我 init 專案」等要為當前資料夾建立專案基礎建設的請求時，請一定要使用此技能。本技能會依這台電腦的工具鏈自動建到最高可用層級：L1 本地（agents.md + handoff.md + CLAUDE.md 橋接）→ L2 GitHub（git init + repo，建立前詢問公開或私有）→ L3 Obsidian（專案詳細筆記）。
---

# 專案初始化技能（三層級自動偵測）

## 步驟 0：技能版本前置檢查（在做下面任何事之前）

安裝副本是舊版時，這個技能會照舊版邏輯跑完而**沒人會發現**——初始化只做一次，用舊版範本建出來的專案骨架會一直錯下去。所以先跑一次比對：

```powershell
& "$HOME\我的雲端硬碟\agents\cross-device-agent-skills\check-sync.ps1" project-init
```

按輸出處理：

| 輸出 | 怎麼做 |
|------|--------|
| 全 `OK` | 直接往下做，**不用回報這一步** |
| `BEHIND` | 源檔自己就是舊的（GDrive 整包還沒同步完）。腳本已中止，此時任何比對結果都不可信。**先告知使用者、建議 `git pull` 後重跑**，別急著同步 |
| `DIRTY` | 掃一眼列出的檔案：都是你認得的改動就繼續；有非預期檔案先停下來查 git |
| `STALE` 且是**你現在跑的工具** | 先告知「本次執行用的是舊版技能，`templates/` 可能也是舊的」，**建議先同步再初始化**。使用者要照舊版繼續也照辦，但不要默默跳過 |
| `STALE` 但是**別的工具** | 這次執行不受影響，只在最後附一句「<工具> 的副本待同步」 |
| 找不到腳本／沒有 PowerShell | 略過，照常往下做 |

> 同步一律跑 `check-sync.ps1 -Sync`（內部用 `Copy-Item` 從磁碟複製，並自動驗證）。**絕不可用 Write/Edit 重建副本**——那會把 context 裡記得的舊內容寫進去，而且事後看起來跟正常同步一模一樣。

## 設計理念

一套技能、三個層級。**這台電腦裝了什麼工具，就自動建到哪個層級**——不用問使用者「你要第幾層級」。

三層資訊的定位與讀取頻率不同：

| 層級 | 平台 | 建立的東西 | 讀取時機 |
|------|------|-----------|---------|
| L1 本地 | 專案資料夾（建議放 GDrive） | `agents.md`（專案藍圖）＋`handoff.md`（交接檔）＋`CLAUDE.md`（橋接檔） | **每個 session 都讀** |
| L2 GitHub | repo（公開／私有由使用者選） | git 版本控制＋雲端備份 | 指定才讀 |
| L3 Obsidian | 第二大腦 vault | `專案工作流程.md`（詳細筆記） | 有需要才讀 |

> **為什麼藍圖叫 `agents.md`，卻還要多一個 `CLAUDE.md`？**
> AGENTS.md 是跨 Agent 開放標準，Codex、Gemini CLI、OpenCode 會自動讀，所以專案藍圖刻意用這個檔名。
> 但 **Claude Code 只讀 `CLAUDE.md`，不讀 `agents.md`**（[官方文件](https://code.claude.com/docs/en/memory)明載）——藍圖放在那裡它也不會載入。
> 解法是官方建議的橋接：建一個 `CLAUDE.md`，第一行寫 `@agents.md` 把藍圖 import 進來。
> 這樣藍圖仍只有一份（不會兩邊分叉），四家 Agent 都吃得到。
> Windows 不用 symlink（要系統管理員或開發者模式），一律用 `@` import。

## 層級偵測（初始化看「這台電腦」有什麼）

依序檢查，決定本次能建到第幾層級：

1. **L1**：無條件可建
2. **L2**：跑 `gh auth status`，成功（已登入 GitHub CLI）→ 可建
3. **L3**：Obsidian MCP 工具（`mcp__obsidian__*`）可用 → 可建

檢查完先告訴使用者：「這台電腦可初始化至第 N 層級」，再開始執行。

## 初始化 SOP（依序執行）

### L1：本地藍圖（永遠執行）

1. **掃描資料夾現況**：列出既有檔案，若已有 `agents.md`、`handoff.md` 或 `CLAUDE.md` → 停下來問使用者是否要覆蓋
2. **詢問使用者**：專案名稱、一句話目標、關鍵時程（沒有就留白，不要硬編）
3. **建立 `agents.md`**：用 `templates/agents.template.md` 為底，填入實際內容；「資料夾結構」區塊由掃描結果自動生成
4. **建立 `handoff.md`**：用 `templates/handoff.template.md` 為底，「目前做到哪」填「專案初始化完成」，更新者填 Agent 名＋電腦名（PowerShell 用 `$env:COMPUTERNAME` 取得）
5. **建立 `CLAUDE.md` 橋接檔**：用 `templates/claude.template.md` 為底。內容只有 import 加上 Claude 專屬區塊——**專案內容一律寫進 `agents.md`，不要複製一份到這裡**（兩份會分叉）：

   ```markdown
   @agents.md

   ## Claude Code 專屬

   （只放 Claude Code 才需要的規範；沒有就留白。專案內容請寫在 agents.md）
   ```

   已有 `CLAUDE.md` 而使用者不要覆蓋時：只在檔案**最上方補一行 `@agents.md`**，其餘內容不動，並告知使用者哪些段落跟 `agents.md` 重複、可自行刪。
6. 若路徑含「雲端硬碟」或「My Drive」→ 提醒使用者確認 Google 雲端硬碟桌面版的同步圖示已打勾（檔案要真的躺在雲端，換電腦才拿得到）

### L2：GitHub（gh 已登入才做，否則跳過並註明）

7. **git 初始化**：
   ```bash
   git init
   git config user.email "changyiwu@gmail.com"
   git config user.name "changyiwu"
   git config windows.appendAtomically false   # GDrive 上跑 git 的必要設定，避免寫入錯誤
   ```
8. **建立 `.gitignore`**（GDrive 專用）：
   ```
   desktop.ini
   *.tmp
   ~$*
   .env
   *.key
   credentials.*
   ```
9. **初始 commit**：`git add .` → `git commit -m "初始化專案：<專案名稱>"`
10. **建立 repo**：問使用者兩件事——
   - 偏好的英文 repo 名
   - **可見度：公開（public）還是私有（private）？** 一定要問，不要自己決定；使用者沒明確回答就用 **private**

   然後依選擇執行（`<可見度>` 填 `--private` 或 `--public`）：
   ```bash
   gh repo create changyiwu/<repo-name> <可見度> --source=. --push
   ```
   選公開前先提醒一句：公開 repo 的內容與 commit 歷史所有人都看得到，確認沒有金鑰、個資或未公開素材再建。
11. **回填 `agents.md`** 同步層級表的 GitHub 欄（repo 網址，並註明公開／私有）

### L3：Obsidian（MCP 可用才做，否則跳過並註明）

12. 在 vault 根目錄建立與專案資料夾**同名**的資料夾
13. 建立 `<資料夾名>/專案工作流程.md`，內容包含：專案背景與詳細脈絡、決策紀錄（為什麼這樣做）、素材與相關筆記連結、🕳️ 踩坑筆記、🗓️ 最近更動紀錄表格（第一行寫今天的初始化）
14. **回填 `agents.md`** 同步層級表的 Obsidian 欄（vault 內路徑）

### 回報

給使用者一個層級 checklist：

```
🏗️ 本專案初始化至第 N 層級
✅ L1 本地：agents.md ＋ handoff.md ＋ CLAUDE.md（橋接，讓 Claude Code 也讀得到藍圖）
✅ L2 GitHub：changyiwu/<repo>（私有／公開，照使用者的選擇寫）
⚠️ L3 Obsidian：未建（這台電腦沒有 Obsidian MCP，之後可在有 Obsidian 的電腦說「補建第三層級」）
```

## 不該做的事

- ❌ 未經確認就覆蓋既有的 `agents.md`／`handoff.md`／`CLAUDE.md`
- ❌ 只建 `agents.md` 就結束（Claude Code 讀不到，一定要補 `CLAUDE.md` 橋接）
- ❌ 把專案內容同時抄進 `agents.md` 和 `CLAUDE.md`（藍圖只留一份，`CLAUDE.md` 只做 import）
- ❌ 電腦沒 gh／Obsidian 時報錯中斷（正確行為：跳過該層級、在回報中註明原因）
- ❌ 把 `.env`、API key 之類敏感檔 commit 進 git
- ❌ 沒問使用者就決定 repo 可見度（一定要問公開或私有；沒回答才用 private 當預設）

## 注意事項

- 所有訊息與檔案內容使用**繁體中文**
- 本 skill 的**原始檔**在 `我的雲端硬碟/agents/cross-device-agent-skills/project-init/`（靠 Google 雲端硬碟跨電腦同步）。**安裝副本共四份**：Claude Code `~/.claude/skills/`、Codex `~/.agents/skills/`、OpenCode `~/.config/opencode/skills/`、Antigravity `~/.gemini/config/skills/`。一律改原始檔，改完跑 README 的同步指令一次覆蓋四份
- 之後的日常循環交給搭檔技能：開工（startup）讀、收工（shutdown）寫

