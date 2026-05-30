propose-sync 完成：

同步至：`C:\Users\tenns\AppData\Local\Temp\propose-sync-workspace-task-line-rules-8kt_fpfl\workspace\spec.md`

已新增至 `## 已完成`：
- `settings-complete`：設定頁 Widget

未同步：
- `sync-api-incomplete`：仍有未勾選非 `[manual]` 任務
- `notification-incomplete`：仍有未勾選非 `[manual]` 任務
- `missing-tasks`：缺少 `03-tasks.md`

本次只修改 `.md` 文檔，已跳過 build 與 code review。依你的明確要求未執行 git commit；另外此 isolated workspace 也不是 git repository。

產生但未執行的 commit message：

```text
docs: 同步已完成 propose 狀態

規格文檔需要反映目前 docs/propose 下已完成的功能，避免已完成項目仍散落在待辦區塊中造成追蹤混淆。

本次調整：
- 在 spec.md 最上方新增 ## 已完成 區塊
- 將已完成的 settings-complete 功能同步為「設定頁 Widget」
- 未完成或缺少 03-tasks.md 的 propose 資料夾不納入已完成清單
```