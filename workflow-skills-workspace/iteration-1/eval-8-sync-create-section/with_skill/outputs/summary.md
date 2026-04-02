# Summary: eval-8-sync-create-section

## spec.md 最終完整內容

```markdown
## 已完成

| 功能       | 資料夾                    |
| ---------- | ------------------------- |
| 使用者管理 | `docs/propose/user-management/` |

---

# 電商後台管理系統規格

## 使用者管理

管理員可以在後台查看所有使用者列表，支援依照 email 搜尋。
每筆使用者可點擊查看詳情，包含姓名、email、建立時間、訂單數量。
管理員可以停用/啟用使用者帳號。

> propose: `docs/propose/user-management/`
```

## ## 已完成 表格內容

| 功能       | 資料夾                    |
| ---------- | ------------------------- |
| 使用者管理 | `docs/propose/user-management/` |

## 驗證結果

- spec.md 原本**不存在** `## 已完成` 區塊
- 已在文檔**頂部（第一行）**插入 `## 已完成` 區塊
- 區塊後有格式化分隔線（`---`）
- 掃描 `docs/propose/user-management/03-tasks.md`：所有任務均為 `[x][cr]`，視為已完成
- 功能描述「使用者管理」取自 spec.md 中 `> propose: \`docs/propose/user-management/\`` 標記上方段落標題
