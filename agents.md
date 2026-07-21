# 跨電腦專案管理三技能（cross-device-agent-skills）（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

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
├─ handoff.md                # 交接檔（每次收工必更新）
├─ project-init/
│  ├─ SKILL.md               # 「初始化專案」技能
│  └─ templates/
│     ├─ agents.template.md  # 專案藍圖範本
│     └─ handoff.template.md # 交接檔範本
├─ startup/SKILL.md          # 「開工」技能
├─ shutdown/SKILL.md         # 「收工」技能
└─ .claude/settings.local.json
```

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | https://github.com/changyiwu/cross-device-agent-skills （公開） | 指定時 |
| L3 | Obsidian | `cross-device-agent-skills/專案工作流程.md` | 有需要時 |

## 工作約定

- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- **本資料夾是技能原始檔**。改動一律改這裡，改完跑 README 的同步指令，一次覆蓋四份安裝副本（Claude Code／Codex／OpenCode／Antigravity）
- 編輯 `SKILL.md` 時不可存成含 BOM 的 UTF-8，否則 frontmatter 解析失敗、技能觸發不了
