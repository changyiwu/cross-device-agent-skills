# 跨電腦專案管理三技能（cross-device-agent-skills）

> 三師爸「AI Agent 基本功」EP06 懶人包：讓你的專案在**任何電腦、任何 Agent** 之間無縫接續。
> 三個口令搞定一切：「**初始化專案**」「**開工**」「**收工**」。

## 這包裡有什麼

| 技能 | 口令 | 做什麼 |
|------|------|--------|
| `project-init` | 「初始化專案」 | 為專案建立藍圖（agents.md）＋交接檔（handoff.md）＋Claude Code 橋接檔（CLAUDE.md），有 GitHub 就順便建 repo（會問你要公開還是私有），有 Obsidian 就建詳細筆記 |
| `startup` | 「開工」 | 讀藍圖＋交接檔，回報上次做到哪（含「上次在哪台電腦收工」）、git 狀態、建議下一步 |
| `shutdown` | 「收工」 | 更新藍圖進度、改寫交接檔、git commit + push、詳細紀錄寫進 Obsidian |

## 三個層級：工具裝到哪，技能就做到哪

這三個技能會**自動偵測**你的工具鏈，不用選版本：

| 層級 | 需要安裝 | 你會得到 |
|------|---------|---------|
| **L1 本地** | 什麼都不用（建議專案放 Google 雲端硬碟資料夾） | `agents.md`＋`handoff.md`＋`CLAUDE.md`（橋接），跨電腦靠雲端硬碟同步 |
| **L2 +GitHub** | [GitHub CLI](https://cli.github.com/)（`gh auth login` 登入） | 版本控制＋雲端備份，貼網址就能分享專案 |
| **L3 +Obsidian** | Obsidian＋Obsidian MCP | 專案詳細筆記（第二大腦） |

三層資訊的讀取頻率不同——這是整套設計的核心：

- `agents.md`＋`handoff.md`：**每個 session 都讀**（放交接必需的精簡資訊）
- GitHub：**指定才讀**（備份與歷史）
- Obsidian：**有需要才讀**（完整脈絡與細節）

## 安裝

```bash
git clone https://github.com/mathruffian-dot/cross-device-agent-skills.git
```

把 `project-init/`、`startup/`、`shutdown/` 三個資料夾複製到你的全域技能目錄：

- Claude Code：`~/.claude/skills/`

然後跟你的 Agent 說一句：

> 「把剛裝的三個技能裡的 `<你的GitHub帳號>` 和 `<你的email>` 占位符，換成我的 GitHub 帳號和 email」

（只有 `project-init` 會用到，L1 使用者可跳過這步。）

### 本副本的設定（changyiwu）

- 占位符已填：GitHub 帳號 `changyiwu`、email `changyiwu@gmail.com`
- **原始檔**：`我的雲端硬碟/agents/cross-device-agent-skills/`（靠 Google 雲端硬碟跨電腦同步）

四個 Agent 工具的技能格式相同（`SKILL.md` + YAML frontmatter），所以**同一份檔案直接共用**，安裝副本共四份：

| 工具 | 全域技能目錄 |
|------|-------------|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Antigravity | `~/.gemini/config/skills/` |

改動一律動原始檔，改完跑這段一次覆蓋四份。**跑之前先確認 worktree 乾淨**：

```bash
git diff HEAD --stat
```

沒列出非預期的改動再往下跑。GDrive 偶爾會餵出過期的檔案內容（磁碟讀到舊 bytes，但 git 的 HEAD 已是新版），這時直接同步等於**把四份副本一起降版**——只看檔案內容或時間戳看不出來，一定要問 git。

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

換一台電腦時，等 GDrive 同步完再跑同一段指令即可（該電腦沒裝的工具，把對應那行從 `$dests` 拿掉）。

> ⚠️ **絕不可請 Agent 用 Write/Edit 重建副本**——那會把它 context 裡記得的舊內容寫進去，事後看起來跟正常同步一模一樣，只有比對才抓得到。同步一律走上面那段 `Copy-Item`（從磁碟複製）。在「之前已開過的舊對話」裡要求同步時風險最高。

### 步驟 0：`chezmoi status` 前置檢查

三個技能的 SKILL.md 都在「步驟 0」跑一次這行，確認本機 dotfile 沒有未處理的漂移：

```powershell
if (Get-Command chezmoi -ErrorAction SilentlyContinue) { chezmoi status } else { "chezmoi 未安裝，略過此步" }
```

- **沒有任何輸出** → 一致，技能照常往下做，不佔版面回報
- **印出任何一行** → 停下來，把原始輸出貼給你再問怎麼處理（`chezmoi apply` 覆蓋本機／`chezmoi add` 收編本機改動），Agent 不自己決定
- **沒裝 chezmoi** → 整步略過，不影響技能執行

這是為了補一個盲點：安裝副本落後或被就地改過時，技能會照舊版邏輯默默跑完，沒人會發現。有用 chezmoi 管 dotfile 的電腦就順便有了這道檢查，沒用的電腦維持原本行為。

> ⚠️ `chezmoi status` 比的是「本機檔案 vs chezmoi source」，跟上面那段 `Copy-Item`（GDrive 原始檔 → 四份安裝副本）是兩條不同路徑。要讓步驟 0 真的看得到技能副本的漂移，得先把那四個技能目錄納入 chezmoi 管理。

> ⚠️ 編輯 SKILL.md 時**不要存成含 BOM 的 UTF-8**。開頭的 `EF BB BF` 會讓 frontmatter 解析失敗，技能雖然載入得了但描述變成 `---`、觸發不了。

## 典型的一天

```
早上（家裡電腦）
  你：「開工」
  Agent：📂 專案 xxx（第 2 層級）
         📘 上次做到哪：完成了報名表單（昨天 22:10，Claude Code @ 學校電腦）
         ⚠️ 上次在另一台電腦收工，GDrive 已同步完成
         ➡️ 建議下一步：1. 接 Firebase 寫入 …

  （工作中……）

晚上
  你：「收工」
  Agent：✅ L1：agents.md 進度已更新、handoff.md 已改寫
         ✅ L2：已 commit + push「新增報名表單 Firebase 寫入」
```

## 三個核心檔案

- **`agents.md`**（專案藍圖）：用 AGENTS.md 開放標準命名——Codex、Gemini CLI、OpenCode 都會自動讀，換 Agent 不用改檔案
- **`handoff.md`**（交接檔）：記錄「目前做到哪／下一步／注意事項／**最後更新者＋電腦名＋有沒有 push**」。不管是**換電腦**還是**換 Agent** 接手，都先讀這個檔
- **`CLAUDE.md`**（橋接檔）：**Claude Code 只讀 `CLAUDE.md`，不讀 `agents.md`**（[官方文件](https://code.claude.com/docs/en/memory)明載），所以要用一行 `@agents.md` 把藍圖 import 進來。藍圖仍只有一份，四家 Agent 都吃得到

```markdown
@agents.md

## Claude Code 專屬
（只放 Claude 專屬規範；專案內容一律寫在 agents.md）
```

> 官方另一個做法是 `ln -s AGENTS.md CLAUDE.md`，但 Windows 建 symlink 要系統管理員或開發者模式，所以一律用 `@` import。
> 驗證方式：在 Claude Code 裡跑 `/context`，看 **Memory files** 有沒有列到 `CLAUDE.md`。

範本在 `project-init/templates/`，初始化技能會自動套用。

## 常見問題

**Q：專案資料夾一定要放 Google 雲端硬碟嗎？**
L1 的跨電腦同步就是靠雲端硬碟桌面版（要裝應用程式，不能只用網頁版）。不放 GDrive 也能用這三個技能，但跨電腦就得完全依賴 L2 的 git push／pull。

**Q：在 GDrive 資料夾跑 git 會出錯？**
初始化技能會自動設定 `git config windows.appendAtomically false`，這是 GDrive＋git 的已知坑。

**Q：兩台電腦可以同時開工同一個專案嗎？**
不建議——GDrive 會產生衝突副本。開工技能會顯示上次收工的電腦與時間，幫你避開這個情況。

**Q：我只有其中一台電腦裝 Obsidian，怎麼辦？**
沒關係，這正是自動偵測的用途：沒 Obsidian 的電腦收工時會在 handoff.md 註明「L3 未更新」，回到有 Obsidian 的電腦再補。

---

📺 完整教學：三師爸「AI Agent 基本功」EP06——如何跨電腦進行你的專案
