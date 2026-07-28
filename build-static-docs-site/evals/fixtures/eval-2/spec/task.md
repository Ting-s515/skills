# Eval 2 輸入說明

`repository/` 是待處理專案根目錄。建立網站時需涵蓋：

- `A+B.md` 與 `A B.md` 的 slug 碰撞風險。
- `unicode-path.json` 內 `é.md`（NFC）與 `e\u0301.md`（NFD）的 Unicode canonical-equivalent 邏輯路徑風險。
- `docs/unicode-composed.md` 與 `docs/unicode-decomposed.md` 是上述案例的可攜式內容來源；測試文件 ID 時直接傳入 manifest 的 `logicalPath`，不要在檔案系統建立兩個等價路徑。
- `入門.md` 指向 `進階.md#操作流程` 的跨文件連結。
- Mermaid 一般閱讀與 dialog 放大互動。
