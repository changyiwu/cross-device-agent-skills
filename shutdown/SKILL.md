---
name: shutdown
description: 收工同步助手（三層級自動偵測）。當使用者說「收工」、「結束了」、「下班」、「準備換電腦」、「同步」、「先到這裡」、「換電腦繼續做」等任何要結束工作並保存進度的請求時，請一定要使用此技能。本技能會更新 agents.md 進度與 handoff.md 交接檔、git commit + push、把詳細紀錄寫進 Obsidian，確保下次（或在另一台電腦、或換一個 Agent）打開能無縫接續。
---

# 收工同步助手（三層級）

## 步驟 0：dotfile 狀態前置檢查（在做下面任何事之前）

安裝副本被改過或落後時，這個技能會照舊版邏輯跑完而**沒人會發現**。所以先問一次 chezmoi：

```powershell
if (Get-Command chezmoi -ErrorAction SilentlyContinue) { chezmoi status } else { "chezmoi 未安裝，略過此步" }
```

按輸出處理：

| 輸出 | 怎麼做 |
|------|--------|
| 沒有任何一行 | 一致，直接往下做，**不用回報這一步** |
| 印出任何一行 | **停下來**，把原始輸出貼給使用者再問怎麼處理。左欄＝source 有變動待 `chezmoi apply`；右欄＝本機檔案被改過，要 `chezmoi add` 收編或用 `apply` 覆蓋。**不要自己決定跑哪一個** |
| `chezmoi 未安裝，略過此步` | 這台電腦沒裝，略過，照常往下做 |

> 技能原始檔改完要同步四份安裝副本時，用下面「收工的專案是技能 repo 本身時」那段的 `Copy-Item`（從磁碟複製）。**絕不可用 Write/Edit 重建副本**——那會把 context 裡記得的舊內容寫進去，而且事後看起來跟正常同步一模一樣。

---

對話結束前，把這次的工作保存到專案建到的每一層：

| 層級 | 收工動作 | 給誰看 |
|------|---------|--------|
| L1 本地 | 更新 `agents.md` 進度＋改寫 `handoff.md` | 下一個 session 的任何 Agent、任何電腦 |
| L2 GitHub | commit + push | 版本歷史＋雲端備份 |
| L3 Obsidian | 詳細紀錄寫進 `專案工作流程.md` | 未來需要完整脈絡的自己 |

## 核心原則

1. **開工是「讀」、收工是「寫」**——handoff.md 是收工的必寫項，這是跨電腦／跨 Agent 交接的生命線
2. **不在 vacuum 中執行**——先從對話脈絡盤點今天做了什麼
3. **只動需要動的**——沒實質進度（只是問問題、沒改檔案）就不跑同步
4. **有疑問先問人**——commit 前先給訊息草稿等點頭；不確定要不要 add 的檔案先問
5. **精簡與詳細分家**——handoff.md 只放交接必需資訊，完整脈絡（決策原因、踩坑細節）寫 Obsidian，兩邊不重複

## 層級偵測（收工看「這個專案」建到哪層）

- **L1**：專案有 `agents.md`／`handoff.md` → 更新（沒有就提議先跑「初始化專案」）
- **L2**：專案有 `.git` → commit + push
- **L3**：`agents.md` 登記了 Obsidian 路徑，且這台電腦的 Obsidian MCP 可用 → 寫詳細紀錄

> 低層級電腦打開高層級專案：做得到的照做，做不到的在 handoff.md 註明（例：「本次在無 Obsidian 的電腦收工，L3 筆記未更新」），回到高層級電腦時補。

## 收工 SOP（依序執行）

### L1：更新藍圖與交接檔（永遠執行）

1. **盤點本次成果**：從對話歷史摘要——完成了哪些檔案、做了什麼決定、踩了什麼坑
2. **更新 `agents.md`**：
   - 路線圖 checklist：勾掉完成項、新增發現的待辦
   - 「資料夾結構」有新增檔案就補
3. **改寫 `handoff.md`**（整份重寫，不是往下堆）：
   - ⏯️ 目前做到哪：本次最後完成的動作
   - 🚦 目前狀態：可運行？哪些做一半？
   - ➡️ 下一步：具體、可執行的 1-3 項
   - ⚠️ 注意事項：新踩的坑、暫時 workaround
   - 🕐 最後更新：時間＋更新者（Agent 名 @ `$env:COMPUTERNAME`）＋ Git push 狀態（先寫「待推」，L2 完成後回填）

### L2：git 同步（專案有 `.git` 才做）

4. `git status --short` 看變動 → 擬**繁體中文** commit 訊息（標題：動詞＋對象；正文 3-5 條 bullet 描述變動＋為什麼）→ **給使用者過目，點頭再 commit**
5. commit → `git push`
6. **回填 handoff.md 的 Git push 欄**：成功 → `✅ 已推`；失敗 → `❌ 未推（原因）`，並在回報中標紅提醒（沒推成功，另一台電腦就拿不到 GitHub 備份）
7. 不要 add：`.claude/`、`.env`、API key、untracked 的不明新檔（先問）

### L3：Obsidian 詳細紀錄（可用才做）

8. 更新 `<vault>/<資料夾名>/專案工作流程.md`——**只在 `project-init` 定義的五個區塊內就地增修，絕不在檔尾附加新區塊或新表格**（附加式寫法正是筆記格式跑掉的元兇）：
   - 「🗓️ 最近更動紀錄」：**在既有的同一張表**加一行（日期＋摘要＋同步狀態）。全篇只能有這一張表；若發現多張表或「（本次）」之類的重複表／重複區塊，順手合併成一張。
   - 「🕳️ 踩坑筆記」：有新坑就依分類補（含原因與解法，這裡寫詳細版）
   - 「決策紀錄」：本次做了什麼取捨、為什麼（handoff 不放這些，放這裡）
   - 「專案背景」「素材與相關筆記連結」：有變動才改，沒有就不動
   - ❌ **不要**在 L3 寫「目前狀態／下一步／上次做到哪」——那是 `handoff.md` 的職責。L3 永遠維持五段結構：專案背景與詳細脈絡、決策紀錄、素材與相關筆記連結、🕳️ 踩坑筆記、🗓️ 最近更動紀錄
9. 表格超過 30 行 → 提醒使用者歸檔到 `歷史日誌.md`

### 回報（層級 checklist）

```
✅ L1 本地：agents.md 進度已更新、handoff.md 已改寫（更新者：<Agent> @ <電腦名>）
✅ L2 GitHub：<repo> 已 commit + push（<commit 標題>）
✅ L3 Obsidian：專案工作流程.md 已補紀錄
⚠️ 手動處理：<例：本次新增了 ~/.xxx_api_key，另一台電腦要手動建>
```

沒做到的項目用 ⚠️ 或 ❌ 並說明原因。

### 收工的專案是技能 repo 本身時（`我的雲端硬碟/agents/cross-device-agent-skills/`）

安裝副本共四份（Claude Code／Codex／OpenCode／Antigravity），源檔改了但副本沒跟上，這台電腦跑的就還是舊版。

> 這一節跟開頭的「步驟 0」**不是同一件事，兩者都要做**——差別在職責：
>
> - **步驟 0**（技能開始時）：只**回報**「本機 dotfile 現在對不對得上」，不負責同步。而且它一個技能只跑一次，跑完之後才發生的編輯（含收工自己改的檔）它看不到。
> - **這一節**（所有編輯都結束後）：唯一會**真的執行同步**的環節，關心的是「下一個 session／下一台電腦／下一個 Agent 會不會拿到舊版」。

**不要靠「這次有沒有改」的印象判斷**——過去漏跑的漂移，只有實際覆蓋一次才補得回來。

commit 完之後，先確認源檔本身可信（GDrive 可能餵出過期內容，拿舊源檔同步等於把四份副本一起降版）：

```powershell
git diff HEAD --stat
git fetch origin; git rev-list HEAD..origin/master --count
```

`git diff HEAD --stat` 沒列出非預期改動、且落後數是 `0`，才往下覆蓋四份副本：

```powershell
$src = "$HOME\我的雲端硬碟\agents\cross-device-agent-skills"
$dests = @(
  "$HOME\.claude\skills",
  "$HOME\.agents\skills",
  "$HOME\.config\opencode\skills",
  "$HOME\.gemini\config\skills"
)
foreach ($d in $dests) {
  foreach ($s in 'project-init','startup','shutdown') {
    Copy-Item "$src\$s" "$d\" -Recurse -Force
  }
}
```

這台電腦沒裝的工具，把對應那行從 `$dests` 拿掉。落後數不是 `0` 就**先 `git pull` 再同步**。

⚠️ **不要用 Write/Edit 重建副本**——那會把 context 裡記得的舊內容寫進去，事後看起來跟正常同步一模一樣，只有比對才抓得到。

## 不該做的事

- ❌ 對「沒實質進度」的對話也跑同步
- ❌ 沒更新 handoff.md 就收工（那是下次開工的唯一線索）
- ❌ commit message 寫「更新」、「修改」這種沒資訊的字
- ❌ 自動 add untracked 的新檔或敏感檔（要使用者確認）
- ❌ 把該寫進 Obsidian 的長篇細節塞進 handoff.md（交接檔要保持一頁內讀完）

## 與開工（startup）的對偶關係

| 面向 | 收工 | 開工 |
|------|------|------|
| agents.md / handoff.md | **寫入** | **讀出** |
| Git 動作 | add + commit + push | status + fetch（不 pull） |
| Obsidian | 寫詳細紀錄 | 只列路徑、需要才讀 |
| 對外副作用 | 推 GitHub、改檔案 | 無 |

## 注意事項

- 所有訊息使用**繁體中文**
- GDrive 內的 repo 首次操作若遇 git 寫入錯誤：`git config windows.appendAtomically false`
- **GDrive 上的 repo，一律以 git 為準、不以檔案內容為準**：GDrive 可能回傳過期內容，導致「讀檔看起來是舊版、`git status` 卻乾淨」。判斷版本用 `git diff HEAD`／`git log`，不要靠讀檔或看時間戳。`git status` 出現 `MM` 但 `git diff HEAD` 是空的，通常只是 LF/CRLF 差異，用 `git add --renormalize .` 消掉即可
- 本 skill 的**原始檔**在 `我的雲端硬碟/agents/cross-device-agent-skills/shutdown/`（靠 Google 雲端硬碟跨電腦同步）。**安裝副本共四份**：Claude Code `~/.claude/skills/`、Codex `~/.agents/skills/`、OpenCode `~/.config/opencode/skills/`、Antigravity `~/.gemini/config/skills/`。一律改原始檔，改完跑 README 的同步指令一次覆蓋四份

