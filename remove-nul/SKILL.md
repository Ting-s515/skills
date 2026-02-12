---
name: remove-nul
description: 刪除 Windows 環境下因誤操作產生的 nul 保留裝置名稱檔案，使用 Git Bash 的 rm -f 指令繞過 Windows 限制。
---

# 刪除 nul 檔案

## 背景說明

在 Windows 環境中，`nul` 是系統保留的裝置名稱（類似 `con`、`aux`、`prn` 等），無法透過一般方式（如 `del`、`PowerShell Remove-Item`、`git rm`）刪除。需要透過 Git Bash 的 POSIX 檔案操作來繞過此限制。

## 執行流程

1. **確認檔案存在**：執行 `git status --short -- nul` 確認 `nul` 檔案存在於工作目錄中
2. **刪除檔案**：在 Git Bash 環境下執行 `rm -f nul`
3. **驗證結果**：再次執行 `git status --short -- nul` 確認檔案已被移除

## 指令

```bash
# 步驟 1：確認檔案存在
git status --short -- nul

# 步驟 2：刪除 nul 檔案（Git Bash 環境下執行）
rm -f nul

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
| `rm -f nul`（Git Bash） | 成功 | Git Bash 使用 POSIX 檔案操作，不受 Windows 保留名稱限制 |

## 補充說明

- 此技能適用於所有 Windows 保留裝置名稱檔案（`nul`、`con`、`aux`、`prn`、`com1`~`com9`、`lpt1`~`lpt9`）
- 必須在 Git Bash 環境下執行，不適用於 cmd 或 PowerShell
