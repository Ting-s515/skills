---
name: remove-nul
description: >
  刪除名為 nul、con、aux、prn、com1~com9、lpt1~lpt9 的異常檔案，並依 Windows 或 macOS/Linux 選擇安全指令。
  Windows 會把這些名稱視為保留裝置名稱，需使用 Git Bash 的 POSIX 檔案操作；macOS/Linux 則按一般檔案處理。
  當使用者遇到以下情境時必須載入此技能：git status 顯示有 nul 檔案、想刪除 nul 但 del/PowerShell/git rm 都失敗、
  看到 "Permission denied" 錯誤無法刪除某個奇怪的檔案、詢問「remove nul file」、「怎麼刪除 nul 檔」、
  「nul 檔案刪不掉」、「Windows 保留裝置名稱怎麼清除」等相關問題。
---

# 刪除保留名稱或同名檔案

## 背景說明

在 Windows 環境中，`nul` 是系統保留的裝置名稱（類似 `con`、`aux`、`prn` 等），無法透過一般方式（如 `del`、`PowerShell Remove-Item`、`git rm`）刪除，需要透過 Git Bash 的 POSIX 檔案操作繞過限制。macOS/Linux 沒有這項保留名稱限制，同名項目可按一般檔案刪除。

## 執行流程

1. **確認目標與平台**：執行 `git status --short -- nul`，並確認目前 shell 所在的作業系統。
2. **刪除檔案**：Windows 使用 Git Bash；macOS/Linux 使用原生 shell。兩者皆執行 `rm -f -- ./nul`。
3. **驗證結果**：再次執行 `git status --short -- nul` 確認檔案已被移除。

## 指令

```bash
# 步驟 1：確認檔案存在
git status --short -- nul

# 步驟 2：Windows 請在 Git Bash 執行；macOS/Linux 使用原生 shell
rm -f -- ./nul

# 步驟 3：驗證刪除結果
git status --short -- nul
```

## 為什麼其他方式無效

| 指令 | 結果 | 原因 |
|------|------|------|
| `git rm nul` | 失敗 | 檔案為 untracked，不在 git 追蹤中 |
| `git clean -f -- nul` | Permission denied | Windows 保護保留裝置名稱 |
| `cmd /c "del \\?\C:\...\nul"` | 無效 | Windows cmd 無法正確處理 |
| `PowerShell Remove-Item` | 失敗 | 無法辨識 `\\?\` 路徑前綴 |
| `rm -f -- ./nul`（Git Bash） | 成功 | Git Bash 使用 POSIX 檔案操作，不受 Windows 保留名稱限制 |

## 補充說明

- Windows 遇到保留裝置名稱時，必須在 Git Bash 執行，不適用於 cmd 或 PowerShell。
- macOS/Linux 不需要 Git Bash；先解析並確認目標是目前 repository 內的單一檔案，再用原生 shell 刪除。
- 其他名稱請把指令中的 `nul` 換成實際檔名，不得使用 glob 或擴大刪除範圍。
