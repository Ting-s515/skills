# Windows Python UTF-8 環境設定

新環境設定必要步驟，確保所有 Python 腳本（含 `run_evals_bdd.py`）預設使用 UTF-8，避免 Windows cp950 編碼問題。

## 設定步驟

1. 按 `Win + S`，搜尋「環境變數」，點選「編輯系統環境變數」
2. 點右下角「環境變數」按鈕
3. 在「使用者變數」區塊點「新增」
4. 填入：
   - 變數名稱：`PYTHONUTF8`
   - 變數值：`1`
5. 按確定 → 確定 → 確定
6. 重開所有終端機視窗（包含 Claude Code）

## 驗證是否生效

```powershell
python -c "import sys; print(sys.flags.utf8_mode)"
```

輸出 `1` 表示設定成功。

## 效果說明

設定後 `sys.flags.utf8_mode` 為 `True`，`run_evals_bdd.py` 的 re-exec 邏輯不會觸發，Python 直接以 UTF-8 模式啟動，無需任何腳本層的額外處理。
