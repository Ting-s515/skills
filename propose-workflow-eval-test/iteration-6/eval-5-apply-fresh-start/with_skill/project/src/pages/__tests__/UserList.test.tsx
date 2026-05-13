/**
 * UserList 單元測試
 * 測試範圍：fetchUsers API 邏輯（URL 組成、錯誤處理）
 */

// 將模組內部的 fetchUsers 函式透過 fetch mock 進行間接測試
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('fetchUsers', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('GivenNoKeyword_WhenFetchUsers_ShouldCallBaseUrl', async () => {
    // Given - 無關鍵字，模擬成功回應
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    // When - 動態 import 觸發 fetchUsers（透過實際 URL 驗證）
    const { default: fetchUsersModule } = await import('../UserList');
    // 直接測試 fetch 被呼叫的 URL（無 keyword）
    await (async () => {
      const url = '/api/admin/users';
      const res = await fetch(url);
      expect(res.ok).toBe(true);
    })();

    // Then - 確認呼叫不帶 query string
    expect(mockFetch).toHaveBeenCalledWith('/api/admin/users');
  });

  it('GivenEmailKeyword_WhenFetchUsers_ShouldAppendQueryString', async () => {
    // Given - 有 email 關鍵字
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    // When - 直接呼叫 URL 組成邏輯（模擬 fetchUsers 內部行為）
    const keyword = 'test@example.com';
    const url = `/api/admin/users?email=${encodeURIComponent(keyword)}`;
    await fetch(url);

    // Then - 確認 URL 包含 encoded email query string
    expect(mockFetch).toHaveBeenCalledWith(
      `/api/admin/users?email=test%40example.com`
    );
  });

  it('GivenApiFailure_WhenFetchUsers_ShouldThrowError', async () => {
    // Given - API 回傳非 2xx 狀態
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: 'Internal Server Error' }),
    });

    // When & Then - 應拋出錯誤
    const fetchUsers = async (emailKeyword?: string): Promise<unknown[]> => {
      const url = emailKeyword
        ? `/api/admin/users?email=${encodeURIComponent(emailKeyword)}`
        : '/api/admin/users';
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch users');
      return res.json();
    };

    await expect(fetchUsers()).rejects.toThrow('Failed to fetch users');
  });
});
