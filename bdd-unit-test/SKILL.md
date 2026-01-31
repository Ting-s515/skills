---
name: bdd-unit-test
description: 當我指定某個檔案需要寫單測時，你會協助我根據 BDD（行為驅動開發）原則撰寫單元測試，確保測試涵蓋所有關鍵行為和邊界條件。
---

# 單元測試撰寫指南（BDD 原則）

## 執行流程

1. **判別語言**：根據檔案副檔名判別程式語言，載入對應範例
2. **分析原始碼**：讀取指定檔案，識別所有公開方法、條件分支、邊界情況
3. **列出測試場景**：使用 BDD 格式列出所有需測試的場景（先輸出給用戶確認）
4. **撰寫測試**：根據確認的場景撰寫測試程式碼
5. **輸出測試檔案**：依據語言規範輸出到正確位置

## 測試範圍

### ✅ 包含
- 純邏輯函數（計算、驗證、轉換）
- 服務層方法（business logic）
- 工具函數（utils/helpers）
- 資料處理（parsing、formatting）  
- 狀態管理邏輯（非 UI 綁定部分）

### ❌ 不包含
- **UI 畫面測試**：不測試 React/Vue 元件的渲染結果、DOM 結構
- **視覺回歸測試**：不測試樣式、佈局、截圖比對
- **E2E 測試**：不測試完整使用者流程、瀏覽器互動
- **整合測試**：不測試多個模組的整合行為

## 語言判別規則

根據目標檔案的副檔名，自動判別語言並載入對應範例：

| 副檔名 | 語言 | 載入範例 |
|--------|------|----------|
| `.ts`, `.tsx` | TypeScript | `examples/typescript-example.test.ts` |
| `.js`, `.jsx` | JavaScript | `examples/typescript-example.test.ts` |
| `.cs` | C# | `examples/csharp-example-test.cs` |
| `.java` | Java | `examples/java-example-test.java` |
| `.py` | Python | `examples/python-example-test.py` |

**執行步驟：**
1. 取得目標檔案的副檔名
2. 根據上表判別語言
3. 讀取對應的 example 檔案作為撰寫測試的參考
4. 依照該語言的規範（框架、命名、輸出位置）產出測試

## BDD 核心原則

### Given-When-Then 結構
```
Given [前置條件/初始狀態]
When  [執行的動作/觸發事件]
Then  [預期結果/驗證行為]
```

### 測試場景分類（必須涵蓋）
| 分類 | 說明 | 範例 |
|------|------|------|
| ✅ Happy Path | 正常流程、預期輸入 | 有效參數、正確格式 |
| ⚠️ Edge Cases | 邊界條件 | 空值、最大/最小值、零 |
| ❌ Error Cases | 異常處理 | 無效輸入、例外拋出 |
| 🔄 State Changes | 狀態轉換 | 初始化、重置、更新 |

### 測試命名規範
採用 `Given條件_When動作_Should預期行為` 格式：
```
GivenNoItems_WhenGetList_ShouldReturnEmptyList
GivenNullInput_WhenValidate_ShouldThrowException
GivenItemsExist_WhenCalculateTotal_ShouldReturnCorrectSum
```

---

## 語言別測試規範

### 🟨 JavaScript/TypeScript (.ts, .tsx)
| 項目 | 規範 |
|------|------|
| 框架 | Jest |
| 檔案命名 | `[ComponentName].test.tsx` |
| 輸出位置 | 同目錄的 `__tests__/` 資料夾 |
| Mock 工具 | `jest.mock()` |
| 斷言風格 | `expect(result).toBe(expected)` |

**結構範例：**
```typescript
describe('模組/元件名稱', () => {
  describe('方法名稱', () => {
    it('Given[條件]_When[動作]_Should[預期行為]', () => {
      // Given - 準備測試資料
      const input = { ... };

      // When - 執行被測方法
      const result = targetMethod(input);

      // Then - 驗證結果
      expect(result).toEqual(expected);
    });
  });
});
```

### 🟦 C# (.cs)
| 項目 | 規範 |
|------|------|
| 框架 | xUnit |
| 檔案命名 | `[ClassName]Test.cs` |
| 輸出位置 | 對應的 `.Tests` 專案資料夾 |
| Mock 工具 | Moq |
| 斷言風格 | `Assert.Equal(expected, actual)` |

**結構範例：**
```csharp
public class UserServiceTests
{
    [Fact]
    public void GivenUserExists_WhenGetUser_ShouldReturnUser()
    {
        // Given
        var mockRepo = new Mock<IUserRepository>();
        mockRepo.Setup(r => r.GetById(1)).Returns(new User { Id = 1 });
        var service = new UserService(mockRepo.Object);

        // When
        var result = service.GetUser(1);

        // Then
        Assert.NotNull(result);
        Assert.Equal(1, result.Id);
    }
}
```

### ☕ Java (.java)
| 項目 | 規範 |
|------|------|
| 框架 | JUnit 5 / TestNG |
| 檔案命名 | `[ClassName]Test.java` |
| 輸出位置 | `src/test/java/` 對應套件路徑 |
| Mock 工具 | Mockito, MockK (Kotlin) |
| 斷言風格 | AssertJ: `assertThat(result).isEqualTo(expected)` |

**結構範例：**
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @InjectMocks
    private OrderService orderService;

    @Test
    @DisplayName("應該在訂單存在時返回訂單")
    void GivenOrderExists_WhenGetOrder_ShouldReturnOrder() {
        // Given - 設定 mock 行為
        Order expected = new Order(1L, "item");
        when(orderRepository.findById(1L)).thenReturn(Optional.of(expected));

        // When - 執行被測方法
        Order result = orderService.getOrder(1L);

        // Then - 驗證結果
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
    }
}
```

### 🐍 Python (.py)
| 項目 | 規範 |
|------|------|
| 框架 | pytest / unittest |
| 檔案命名 | `test_[module_name].py` |
| 輸出位置 | `tests/` 資料夾，保持與 src 相同結構 |
| Mock 工具 | `unittest.mock`, `pytest-mock` |
| 斷言風格 | `assert result == expected` |

**結構範例：**
```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    """UserService 單元測試"""

    def test_GivenUserExists_WhenGetUser_ShouldReturnUserData(self):
        """應該在用戶存在時返回用戶資料"""
        # Given
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = {"id": 1, "name": "Test"}
        service = UserService(mock_repo)

        # When
        result = service.get_user(1)

        # Then
        assert result is not None
        assert result["id"] == 1
```

---

## Mock 使用原則

### 何時使用 Mock
- 📦 外部套件依賴（npm packages、第三方函式庫）
- 🌐 外部 API 呼叫（HTTP requests）
- 🗄️ 資料庫操作
- 📁 檔案系統存取
- ⏰ 時間相關函數（Date.now, datetime）
- 🎲 隨機數生成

### Mock 最佳實踐
1. **只 Mock 直接依賴**：不要 Mock 被測單元的內部實作
2. **驗證互動**：確認 Mock 被正確呼叫（次數、參數）
3. **重置狀態**：每個測試後清理 Mock 狀態
4. **避免過度 Mock**：過多 Mock 可能表示耦合度太高

---

## 輸出格式

執行此 skill 時，請依序輸出：

### 1️⃣ 場景分析
```markdown
## 📋 測試場景分析

**目標檔案：** `path/to/file.ts`
**識別的公開方法：** methodA, methodB, methodC

### 測試場景列表

| # | 方法 | 場景類型 | 描述 |
|---|------|----------|------|
| 1 | methodA | ✅ Happy | 當輸入有效時應返回正確結果 |
| 2 | methodA | ⚠️ Edge | 當輸入為空時應返回空陣列 |
| 3 | methodA | ❌ Error | 當輸入為 null 時應拋出例外 |

確認以上場景後，我將開始撰寫測試。
```

### 2️⃣ 測試程式碼
依據確認的場景，輸出完整測試檔案，包含：
- 必要的 import
- 完整的測試結構
- 每個測試的 Given/When/Then 註解

---

## 參考範例

根據判別的語言，讀取對應的範例檔案：

- **TypeScript/JavaScript**: `examples/typescript-example.test.ts`
- **C#**: `examples/csharp-example-test.cs`
- **Java**: `examples/java-example-test.java`
- **Python**: `examples/python-example-test.py`

**注意**：撰寫測試前必須先讀取對應語言的範例，確保遵循一致的風格與結構。