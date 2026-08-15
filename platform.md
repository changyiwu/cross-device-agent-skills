# 跨平台約定（Windows ↔ macOS）

> 同一份技能／腳本要在兩個平台都能跑時，這裡是唯一權威。
> 時效性等級同 `agents.md`：**長期有效**，只有規則本身變了才改；逐次的踩坑經過留 Obsidian。
> **這份檔是邊撞邊長的**——先在 mac 上實測，撞到什麼才補什麼，不預先寫規格。

## 執行環境

一律 **pwsh 7**（macOS：`brew install --cask powershell`），不可退回 Windows PowerShell 5.1。

## 路徑原則（只有一條）

**路徑一律相對 cwd，或從 cwd 往上找；不要解析「雲端硬碟根」。**

實際會用到的存取模式只有這兩種，而兩種都天生跨平台：

- 技能操作的是**當前專案目錄**，agent 啟動時 cwd 就是它
- 要找上層共用資料夾（例如 `.skill-install/`）就**從 cwd 往上走**（見 `sync-skills` 步驟 4）

跨專案互相引用時**不要寫絕對路徑**，改成相對路徑或往上找——這樣就永遠不需要知道雲端硬碟掛在哪。

寫程式碼時的三條配套規則：

- 組路徑一律 `Join-Path`，不要出現字面 `\`
- 正則裡的分隔符一律 `[\\/]`
- 需要單一分隔符字元時用 `[IO.Path]::DirectorySeparatorChar`

## 四個坑（都是「不報錯」型的）

這四個的共同特徵：**失敗時沒有任何錯誤訊息**，所以要先知道才找得到。

### 1. `$IsWindows` 在 5.1 是 `$null`，不是 `$false`

任何 `if ($IsWindows) {...} else {...}` 在 5.1 上會**直接掉進 macOS 分支**，然後回報「找不到 X」——失敗原因指向完全錯誤的方向。有分支就先擋：

```powershell
if ($null -eq $IsWindows) { throw '需要 PowerShell 7；5.1 沒有 $IsWindows，會靜默走錯分支' }
```

### 2. `$env:COMPUTERNAME` 在 macOS 是空字串

一律用 `[Environment]::MachineName`。用錯的兩個後果都不報錯：

- `handoff.md` 的「最後更新者 @ 電腦名」寫出空白，跨機接手時看不出上次是哪台
- `sync-skills` 步驟 7 的 `"$me.json"` 會生出一個**檔名就叫 `.json`** 的隱藏檔，別台永遠讀不到那台裝了什麼，於是那台的技能全被歸進「都沒裝（八成是刻意的）」

### 3. 中文檔名的 NFD／NFC 差異

macOS 檔案系統用 NFD、Windows 用 NFC，同一個「我的雲端硬碟」在兩邊的 bytes **不同**，字串等值比對會失敗**而路徑其實有效**。

git 的 `core.precomposeunicode` 會在 mac 端轉回 NFC（新版預設開），但要確認：

```powershell
git config --get core.precomposeunicode    # mac 上應為 true
```

比對含中文的路徑時用 `Test-Path`／`Resolve-Path` 判斷實體存在，不要用 `-eq` 比字串。

### 4. macOS 的 APFS 預設不分大小寫

`Skill.md` 與 `SKILL.md` 在 mac 上是同一個檔（Linux 則不是）。**不要靠大小寫區分兩個檔名**，也不要在雲端硬碟上做「只改大小寫」的更名——GDrive 同步這種更名容易產生重複檔或不傳播。

## 編碼：一律 UTF-8 無 BOM

`.md`、`.ps1`、`.py` **全部無 BOM**，沒有例外。

舊規則「`.ps1` 必須含 BOM，否則 PowerShell 5.1 當成 ANSI 讀、中文字串爛掉」**已廢止**——那條的前提是 5.1，而 5.1 不再是支援目標。兩條相反的編碼規則就此收斂成一條。

用 PowerShell 寫檔一律：

```powershell
[IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))
```

不要用 `Set-Content -Encoding UTF8`。

> 既有的 `.ps1` 多數還帶著 BOM。**pwsh 7 讀有 BOM 的檔沒問題**，所以不急著全部重存；處理到哪個專案就順手把那個專案的檔案改成無 BOM 即可。

## 能力分級：不強求對等

跨平台**不等於功能對等**。某個能力在 mac 上沒有對應時，正確行為是**明說**，不是找次級替代品硬湊。

| 能力 | Windows | macOS | 處置 |
|------|---------|-------|------|
| Word／PowerPoint COM 轉檔、截圖 | ✅ | ❌ 無對應 | 標 **Windows-only**，mac 上直接說「本機不支援」並停下 |
| 離線語音備援 | SAPI | `say` | 備援鏈末端換掉；前面的 Edge-TTS 兩層本來就跨平台 |
| 瀏覽器 headless 截圖 | Edge | Chrome／Edge 皆可 | 偵測可用瀏覽器，不寫死執行檔路徑 |
| Tesseract OCR | `C:\Program Files\Tesseract-OCR` | `brew --prefix tesseract` | 一律 `Get-Command tesseract`，不寫死安裝路徑 |
| 套件安裝 | winget | brew | 只有安裝指示分流，其餘步驟共用 |
| chezmoi | 已決定不裝 | — | 不處理 |

實作規範，三條：

1. **技能的〈環境需求〉要寫明平台支援**，不支援時的行為是「講清楚 ＋ 建議替代做法」，**不是靜默降級**——靜默降級會產出看起來正常、其實是次級品的結果，比直接失敗更難發現。
2. **偵測工具用 `Get-Command`，不要寫死安裝路徑。** 兩個平台的安裝位置本來就不同，寫死等於保證有一邊會壞。
3. ⚠️ **不要為了跨平台把 Office COM 換成 LibreOffice。** `share-report/agents.md` 已經驗證過：`soffice` 在 Windows 會因 `socket.AF_UNIX` 直接 `AttributeError`，而且它替換字型導致字寬不同，「文字有沒有溢出」會**判斷錯誤**——那是比不支援更糟的失敗方式。
