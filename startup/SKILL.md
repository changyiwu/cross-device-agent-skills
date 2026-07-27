---
name: startup
description: 開工接續助手（三層級自動偵測）。當使用者說「開工」、「開始工作」、「我來了」、「上次做到哪」、「我們繼續」、「接下來呢」、「接續工作」、「來吧」等任何要接續上次工作的請求時，請一定要使用此技能。本技能會讀取 agents.md 專案藍圖與 handoff.md 交接檔、檢查 git 狀態（含遠端 fetch）、辨識上次是否在另一台電腦收工、建議下一步該做什麼。
---

# 開工接續助手（三層級）

新對話開始時，幫使用者快速進入「上次做到哪」的脈絡，避免從零開始解釋。

## 步驟 0：技能版本前置檢查（在做下面任何事之前）

安裝副本是舊版時，這個技能會照舊版邏輯跑完而**沒人會發現**。所以先跑一次比對：

```powershell
& "$HOME\我的雲端硬碟\agents\cross-device-agent-skills\check-sync.ps1" startup
```

按輸出處理：

| 輸出 | 怎麼做 |
|------|--------|
| 全 `OK` | 直接往下做，**不用回報這一步**（別拿雜訊佔開工報告） |
| `BEHIND` | 源檔自己就是舊的（GDrive 整包還沒同步完）。腳本已中止，此時任何比對結果都不可信。**先告知使用者、建議 `git pull` 後重跑**，別急著同步 |
| `DIRTY` | 掃一眼列出的檔案：都是你認得的改動就繼續；有非預期檔案先停下來查 git |
| `STALE` 且是**你現在跑的工具** | 先告知「本次執行用的是舊版技能」，建議先同步再繼續。使用者要照舊版繼續也照辦，但不要默默跳過 |
| `STALE` 但是**別的工具** | 這次執行不受影響，只在最後附一句「<工具> 的副本待同步」 |
| 找不到腳本／沒有 PowerShell | 略過，照常往下做，別為此中斷開工 |

> 同步一律跑 `check-sync.ps1 -Sync`（內部用 `Copy-Item` 從磁碟複製，並自動驗證）。**絕不可用 Write/Edit 重建副本**——那會把 context 裡記得的舊內容寫進去，而且事後看起來跟正常同步一模一樣。

## 核心原則

1. **開工是「讀」、收工是「寫」**——本技能只讀、只報告，不改任何檔案
2. **不主動 `git pull`**（避免覆蓋本地未 commit 變動，只提醒「要不要 pull」）
3. **30 分鐘內 fetch 過就跳過**（避免單台多對話冗餘）
4. **Obsidian 有需要才讀**——L3 筆記是詳細背景資料，開工預設不讀、只列出路徑
5. 跟收工（shutdown）技能是**對偶關係**：收工存進去、開工讀出來

## 層級偵測（開工看「這個專案」建到哪層）

- **L1**：專案有 `agents.md`／`handoff.md` → 讀
  - 你是 **Claude Code** 且專案有 `agents.md`、卻沒有 `CLAUDE.md`（或 `CLAUDE.md` 裡沒有 `@agents.md`）→ 藍圖這個 session **沒被自動載入**。用 Read 工具把 `agents.md` 讀進來照常開工，並在回報最後提醒：「這個專案缺 `CLAUDE.md` 橋接，要不要補一行 `@agents.md`？」
- **L2**：專案有 `.git` → 做 git 檢查
- **L3**：`agents.md` 同步層級表登記了 Obsidian 路徑，且 Obsidian MCP 可用 → 列出筆記路徑（不主動讀）

> 注意：偵測依據是「專案有什麼」，不是「電腦有什麼」。低層級電腦打開高層級專案時做得到的照做、做不到的註明（優雅降級）。

## 開工 SOP（依序執行）

### L1：讀藍圖與交接檔（永遠執行）

1. **讀 `agents.md`**：專案目標、路線圖進度、工作約定（摘要，不全文倒出）
2. **讀 `handoff.md`**：上次做到哪、目前狀態、下一步、注意事項
3. **檢查「最後更新」欄**：
   - 若**更新者的電腦名 ≠ 這台電腦**（PowerShell 比對 `$env:COMPUTERNAME`）→ 特別標示「⚠️ 上次在另一台電腦（名稱）收工」，並確認 GDrive 同步已完成（看 handoff.md 檔案時間戳是否與交接檔內時間吻合；若本地檔案明顯過舊，提醒等 GDrive 同步完再開工）
   - 若 handoff.md 的更新時間比 agents.md 舊很多 → 提醒「上次可能沒有正式收工」

### L2：git 檢查（專案有 `.git` 才做）

4. **本地狀態**：`git status --short`
   - clean → 「本地工作區乾淨」
   - 有未 commit 變動 → 列出，提醒「上次有未完成的修改，要繼續還是放棄？」
5. **遠端狀態**（30 分鐘判斷）：
   ```bash
   [ -n "$(find .git/FETCH_HEAD -mmin -30 2>/dev/null)" ] || git fetch origin 2>/dev/null
   BEHIND=$(git rev-list HEAD..origin/HEAD --count 2>/dev/null || echo 0)
   ```
   - `BEHIND` > 0 → 提醒「遠端有 N 個新 commit，要 `git pull` 嗎？」**不主動 pull**
6. **交叉比對防呆**：若 handoff.md 寫「Git push：✅」但遠端沒有對應的新 commit → 警告「上次收工可能沒推成功，建議先確認再動工」

### L3：Obsidian 筆記（有登記才列，不主動讀）

7. 在報告中列出筆記路徑（例：`<資料夾名>/專案工作流程.md`），註明「需要詳細背景時我再去讀」
8. 只有兩種情況才主動讀：handoff.md 的「下一步」明確指向筆記內容，或使用者要求

### 報告 + 建議下一步

給使用者**結構化摘要**（不要冗長）：

```
📂 專案：<資料夾名>（第 N 層級）
📘 上次做到哪：<handoff 摘要 1-2 句>（<時間>，<更新者> @ <電腦名>）
🔧 本地 git：<clean｜有 N 個未 commit 變動｜—（L1 專案）>
🌐 遠端：<最新｜落後 N commits，建議 git pull｜—>
🧠 Obsidian：<筆記路徑，需要時再讀｜—>
➡️ 建議下一步：
   1. <handoff「下一步」第 1 項>
   2. <可選：第 2 項>

要從哪個方向開始？
```

最後**等使用者選方向**，不要自己擅自繼續。

## 不該做的事

- ❌ 主動 `git pull`（會撞本地未 commit 變動）
- ❌ 修改 `agents.md`／`handoff.md`／Obsidian 筆記（那是收工的事）
- ❌ 沒有交接檔時硬建一個（先問使用者）
- ❌ 開工就把 Obsidian 筆記全文讀進來（違反「有需要才讀」的分層設計）
- ❌ 把藍圖與交接檔內容**全文倒出來**（要摘要、保持精簡）

## 與收工（shutdown）的對偶關係

| 面向 | 收工 | 開工 |
|------|------|------|
| 主要動作 | 摘要今天做什麼 | 摘要上次做什麼 |
| agents.md / handoff.md | **寫入** | **讀出** |
| Git 動作 | add + commit + push | status + fetch（不 pull） |
| Obsidian | 寫詳細紀錄 | 只列路徑、需要才讀 |
| 對外副作用 | 推 GitHub、改檔案 | **無**（只讀、只報告） |

## 注意事項

- 所有訊息使用**繁體中文**
- 本 skill 的**原始檔**在 `我的雲端硬碟/agents/cross-device-agent-skills/startup/`（靠 Google 雲端硬碟跨電腦同步）。**安裝副本共四份**：Claude Code `~/.claude/skills/`、Codex `~/.agents/skills/`、OpenCode `~/.config/opencode/skills/`、Antigravity `~/.gemini/config/skills/`。一律改原始檔，改完跑 README 的同步指令一次覆蓋四份
- 若與全域 CLAUDE.md 的文字版 SOP 重疊：**以本 skill 為準**（skill 是顯性觸發、文字 SOP 是 fallback）

