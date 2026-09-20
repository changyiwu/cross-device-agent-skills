@AGENTS.md

<!--
  本檔是「橋接檔」：Claude Code 自 v2.1.277 起能原生讀 AGENTS.md，
  但預設是二選一——只要有 CLAUDE.md 就只讀 CLAUDE.md、完全不碰 AGENTS.md，
  所以用第一行的 @AGENTS.md 把跨 Agent 專案藍圖 import 進來（不會讀兩次）。
  保留本檔的理由見 AGENTS.md〈工作約定〉：原生讀取有四種場合失效，
  且本檔另有 Claude 專屬規範。專案內容一律寫進 AGENTS.md，避免兩份分叉。
-->

## Claude Code 專屬

- 改技能一律改本資料夾的原始檔，改完說「同步技能」交給 `sync-skills` 技能覆蓋各家安裝副本；**絕不可用 Write/Edit 重建 `~/.claude/skills/` 的安裝副本**
- 驗證橋接是否生效：跑 `/context`，看 **Memory files** 有沒有列到 `CLAUDE.md`（走 import 的情況；原生讀取不會列出，見〈工作約定〉）
