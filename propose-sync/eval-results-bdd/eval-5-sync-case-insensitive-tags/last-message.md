propose-sync 完成。

同步至：[spec.md](</C:/Users/tenns/AppData/Local/Temp/propose-sync-workspace-case-tags-bbm1fso6/workspace/spec.md>)

已新增至 `## 已完成`：
- `mixed-case-complete`

未同步：
- `mixed-case-incomplete`，因為仍有未勾選的非 `[manual]` 任務

驗證已完成：讀回 `spec.md` 確認區塊已插入，並重新檢查兩個 `03-tasks.md` 的完成狀態。Code Review 跳過原因：本次只修改 Markdown 文件。Build 跳過原因：純文檔變更。未執行 git commit：使用者明確要求不要 commit，且此 workspace 不是 git repo。

本次產生但未執行的 commit message：

```text
docs: sync completed propose features

本次調整是依照 propose-sync 規則，將已完成的 propose 功能同步回規格文檔，避免已完成項目仍停留在待處理清單中。

本次調整：
- 在 spec.md 頂部新增 ## 已完成 區塊
- 將 docs/propose/mixed-case-complete/ 同步為已完成
- 保留 mixed-case-incomplete 為未完成，因其仍有未勾選的非 manual 任務
```
