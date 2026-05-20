---
name: gherkin-to-widget-test
description: >
  當使用者提供 Gherkin 規格檔案並要求產出 Flutter Widget Test 時，必須載入此技能。
  從 Gherkin 的每個 Scenario 識別 UI 層驗收條件（Then 步驟描述畫面行為），
  對照 Presentation 層的 Screen 實作，產出使用 Riverpod provider override 的 testWidgets 測試骨架。
  觸發情境包含但不限於：「依照 Gherkin 產出 widget test」、「gherkin-to-widget-test」、「從 Gherkin 寫 widget test」、「補齊 UI 測試」。
  此技能專屬 Flutter/Dart 專案，輸出的測試檔名為 `{feature}_screen_test.dart`，放於 `test/features/{feature}/`。
---

# Gherkin to Widget Test（從 Gherkin 產出 Flutter Widget Test）

## 目的

將 Gherkin 規格檔案中涉及 UI 行為的 Scenario，轉換為可執行的 `testWidgets` 測試：

- 每個含有 UI 層 Then 步驟的 Scenario → 一個 `testWidgets` case
- 使用 `ProviderScope` override 注入 in-memory fake，不依賴真實 SQLite / Drive
- 測試骨架預設有基本斷言，若無法確定對應 Widget，留下 `// TODO: 補充 find.*` 佔位
- 不涵蓋純 domain 層邏輯（那是 AC test 的範疇）

## 輸入

- **Gherkin 檔案路徑**：使用者提供的任意 Gherkin 規格檔案（慣例路徑為 `docs/propose/<feature>/02-gherkin.md`，但不強制）
- **（選用）Screen 實作路徑**：`lib/features/<feature>/presentation/screens/*.dart`
  - 若未提供，自動推導並嘗試讀取

## 執行步驟

### 步驟一：讀取 Gherkin 規格

讀取使用者指定的 Gherkin 規格檔案，識別：
- Feature 名稱
- 每個 Scenario 的標題與 Given/When/Then 步驟
- 標記哪些 Then 步驟屬於 **UI 層行為**（見「UI 層 Then 判斷規則」）

### 步驟二：讀取參考資料

依序讀取以下檔案作為實作參考：

1. **既有 widget test 範例**（本專案已建立的模式）：
   搜尋 `test/features/` 下現有的 `*_screen_test.dart`，取第一個作為風格參考

2. **Support fake repositories**（可用的 in-memory fake）：
   `test/features/support/` 目錄下所有 `in_memory_*.dart`

3. **Screen 實作檔案**（用於識別可 find 的 Widget、Provider）：
   `lib/features/<feature>/presentation/screens/` 下的 `.dart` 檔

4. **Presentation providers**（用於識別需要 override 的 provider）：
   `lib/features/<feature>/presentation/providers/` 下的 `.dart` 檔

### 步驟三：識別 UI 層 Then 步驟

#### UI 層 Then 判斷規則

符合以下任一條件的 Then 步驟，視為 **UI 層行為**，需產出 widget test：

| 關鍵詞 | 範例 | 說明 |
|---|---|---|
| 顯示/不顯示 | `App 顯示匯入失敗訊息` | 畫面有無某文字或元件 |
| header/icon | `首頁 header 顯示同步成功 icon` | 特定 UI 元件的狀態 |
| 表單 | `首頁表單清空或回到預設輸入狀態` | 表單欄位的值或狀態 |
| 引導/對話框 | `App 引導使用者登入 Google` | 彈窗或導引畫面 |
| 空狀態 | `App 不顯示圓餅圖區塊` | 條件性 Widget 的出現與否 |
| 明細/清單 | `App 顯示該月份與該類別下的每筆紀錄` | 清單項目的呈現 |

以下 Then 步驟**不需要** widget test（屬於 domain 層，AC test 已覆蓋）：

- `紀錄寫入本地 SQLite`
- `本機標記為有未同步變更`
- `系統拒絕新增紀錄`
- `App 回傳資料庫錯誤狀態`

### 步驟四：產出 testWidgets 骨架

#### 命名規則

```
T{Scenario序號}_Given{前置條件}_When{動作}_Should{UI預期行為}
```

範例：
```
T3_GivenValidForm_WhenSaved_ShouldResetFormToDefault
T5_GivenGoogleNotSignedIn_WhenOpenHome_ShouldNotShowSyncIcon
```

#### 基本結構

```dart
testWidgets('T{N}_{命名}', (tester) async {
  // Given
  final fakeRepo = InMemoryXxxRepository();
  // ... 準備前置資料

  // When
  await tester.pumpWidget(testApp(repository: fakeRepo));
  await tester.pumpAndSettle();
  // ... 模擬使用者操作（tap、enterText 等）

  // Then
  expect(find.text('...'), findsOneWidget);    // 出現某文字
  expect(find.byIcon(Icons.xxx), findsOneWidget); // 出現某 icon
  expect(find.byType(SomeWidget), findsNothing);  // 某元件不存在
});
```

#### Riverpod Provider Override 模式

```dart
Widget testApp({
  required InMemoryXxxRepository repository,
  InMemoryUnsyncedChangesStore? unsyncedStore,
  SyncStatus syncStatus = SyncStatus.signedOut,
}) {
  return ProviderScope(
    overrides: [
      xxxRepositoryProvider.overrideWithValue(repository),
      if (unsyncedStore != null)
        unsyncedChangesStoreProvider.overrideWithValue(unsyncedStore),
      syncStatusProvider.overrideWithValue(syncStatus),
    ],
    child: const MaterialApp(home: XxxScreen()),
  );
}
```

#### 常用 Flutter Test API

```dart
// 渲染
await tester.pumpWidget(widget);
await tester.pumpAndSettle(); // 等待動畫/async 完成

// 查找
find.text('文字')
find.byType(WidgetType)
find.byIcon(Icons.xxx)
find.byTooltip('tooltip 文字')
find.widgetWithText(ButtonType, '按鈕文字')

// 操作
await tester.tap(finder);
await tester.enterText(finder, '輸入值');
await tester.longPress(finder);

// 斷言
expect(finder, findsOneWidget);   // 恰好一個
expect(finder, findsNothing);     // 不存在
expect(finder, findsNWidgets(n)); // 恰好 n 個
```

### 步驟五：輸出測試檔案

**輸出路徑：** `test/features/<feature>/<feature>_screen_test.dart`

**檔案結構：**

```dart
// 1. imports（flutter_test、flutter_riverpod、feature providers/screens、support fakes）
// 2. void main() { group('<FeatureName>Screen', () { ... }) }
// 3. 每個 UI scenario 一個 testWidgets
// 4. testApp() helper 函式
// 5. 測試資料 helper（fixture）
```

**不產出的部分（留 TODO）：**

若在 Screen 實作中找不到對應的 Widget 或 Provider，保留佔位：
```dart
// TODO: 確認 SyncSuccessIcon widget 名稱後補充 find.*
expect(true, isTrue); // 暫時佔位，避免空測試
```

## 輸出說明

完成後告知使用者：
1. 測試檔案路徑
2. 共產出幾個 testWidgets case
3. 哪些 Then 步驟因無法確認對應 Widget 而留了 TODO
4. 下一步：「執行 `flutter test test/features/<feature>/<feature>_screen_test.dart` 確認測試可運行，再補齊 TODO 斷言」

## 注意事項

- **不重複 AC test 已覆蓋的 domain 邏輯**：widget test 只驗證「畫面呈現」，不驗證資料是否寫入 repository
- **不觸發 JavaScript alert / native dialog**：避免 `showDialog` 類的互動讓測試卡住；若必要，使用 `pumpAndSettle` 後再 `tap` 確認按鈕
- **每個 testWidgets 獨立**：不共享 state，每個 test 建立自己的 `ProviderContainer` 或 `testApp`
- **優先使用 `find.byTooltip` 取代 `find.byKey`**：本專案既有 widget test 用 tooltip 識別按鈕，保持一致
