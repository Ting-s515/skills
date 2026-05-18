# Windows UTF-8 環境設定

新環境必要步驟，確保 Python 腳本（含 `run_evals_bdd.py`）、PowerShell 與 Git Bash 全面使用 UTF-8，避免 Windows cp950 編碼問題。

需設定三層：**Python 層**、**PowerShell 終端機層**、**Git Bash 層**。

---

## 層一：Python 編碼（PYTHONUTF8）

1. 按 `Win + S`，搜尋「環境變數」，點選「編輯系統環境變數」
2. 點右下角「環境變數」按鈕
3. 在「使用者變數」區塊點「新增」
4. 填入：
   - 變數名稱：`PYTHONUTF8`
   - 變數值：`1`
5. 按確定 → 確定 → 確定

**驗證：**
```powershell
python -c "import sys; print(sys.flags.utf8_mode)"
```
輸出 `1` 表示設定成功。

---

## 層二：PowerShell 終端機 UTF-8

### 方法 A：系統地區設定（最全域，影響所有程式）

1. 按 `Win + S`，搜尋「地區設定」，點選「變更地區設定」
2. 點「變更系統地區設定」
3. 勾選「Beta：使用 Unicode UTF-8 提供全球語言支援」
4. 按確定，**重新開機**

**驗證：**
```powershell
chcp
```
輸出 `字碼頁 65001` 表示設定成功。

---

### 方法 B：PowerShell Profile（只影響 PowerShell，不需重開機）

在 PowerShell 輸入：
```powershell
notepad $PROFILE
```

若提示檔案不存在，建立後加入以下內容：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
$OutputEncoding           = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
```

儲存後重開 PowerShell。

**驗證：**
```powershell
[Console]::OutputEncoding
```
輸出 `UTF-8` 表示設定成功。

---

## 層三：Git Bash UTF-8

### Git 全域設定（PowerShell 或 Git Bash 均可執行）

```bash
git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commit.encoding utf-8
git config --global i18n.logoutputencoding utf-8
```

結果寫入 `~/.gitconfig`，兩種終端機執行效果相同。

### ~/.bashrc（在 Git Bash 內執行）

`export` 是 Bash 語法，必須在 **Git Bash** 中執行，不可在 PowerShell 執行。

開啟 Git Bash，編輯 `~/.bashrc`：

```bash
echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=en_US.UTF-8' >> ~/.bashrc
source ~/.bashrc
```

儲存後重開 Git Bash。

**驗證：**
```bash
echo $LANG
git config --list | grep encoding
```
輸出 `en_US.UTF-8` 與各 encoding 設定表示成功。

---

## 建議組合

| 情境 | 建議 |
|------|------|
| 開發機長期使用 | 層一 + 方法 A（系統地區）+ 層三 |
| 不想重開機 | 層一 + 方法 B（Profile）+ 層三 |

---

## 效果說明

三層都設定後：
- `sys.flags.utf8_mode` 為 `True`，`run_evals_bdd.py` 的 re-exec 邏輯不觸發，Python 直接以 UTF-8 啟動
- PowerShell code page 為 65001，終端機顯示中文不亂碼
- Git Bash `LANG=en_US.UTF-8`，commit message、log、檔案路徑顯示正常
