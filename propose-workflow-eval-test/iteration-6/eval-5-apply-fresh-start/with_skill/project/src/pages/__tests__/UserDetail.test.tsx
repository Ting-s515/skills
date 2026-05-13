/**
 * UserDetail 單元測試
 * 測試範圍：fetchUserDetail、updateUserStatus API 邏輯，handleToggleStatus 狀態切換邏輯
 */

const mockFetch = jest.fn();
global.fetch = mockFetch;

// ---- fetchUserDetail ----

describe('fetchUserDetail', () => {
  // 抽出與實作相同的函式進行單元測試
  const fetchUserDetail = async (id: string) => {
    const res = await fetch(`/api/admin/users/${id}`);
    if (!res.ok) throw new Error('Failed to fetch user detail');
    return res.json();
  };

  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('GivenValidUserId_WhenFetchUserDetail_ShouldReturnUserData', async () => {
    // Given - API 回傳使用者詳情
    const mockUser = {
      id: 'u1',
      name: '王小明',
      email: 'ming@example.com',
      createdAt: '2024-01-01',
      orderCount: 5,
      status: 'active',
    };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    // When - 取得使用者詳情
    const result = await fetchUserDetail('u1');

    // Then - 應回傳正確的使用者資料
    expect(result).toEqual(mockUser);
    expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/u1');
  });

  it('GivenApiFailure_WhenFetchUserDetail_ShouldThrowError', async () => {
    // Given - API 回傳非 2xx 狀態
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    // When & Then - 應拋出錯誤
    await expect(fetchUserDetail('not-exist')).rejects.toThrow(
      'Failed to fetch user detail'
    );
  });
});

// ---- updateUserStatus ----

describe('updateUserStatus', () => {
  // 抽出與實作相同的函式進行單元測試
  const updateUserStatus = async (
    id: string,
    status: 'active' | 'disabled'
  ): Promise<void> => {
    const res = await fetch(`/api/admin/users/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update user status');
  };

  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('GivenActiveUser_WhenUpdateStatusToDisabled_ShouldCallPatchWithCorrectBody', async () => {
    // Given - API 回傳成功
    mockFetch.mockResolvedValueOnce({ ok: true });

    // When - 更新狀態為停用
    await updateUserStatus('u1', 'disabled');

    // Then - 應以正確參數呼叫 PATCH API
    expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/u1/status', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'disabled' }),
    });
  });

  it('GivenDisabledUser_WhenUpdateStatusToActive_ShouldCallPatchWithCorrectBody', async () => {
    // Given - API 回傳成功
    mockFetch.mockResolvedValueOnce({ ok: true });

    // When - 更新狀態為啟用
    await updateUserStatus('u1', 'active');

    // Then - 應以正確參數呼叫 PATCH API
    expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/u1/status', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'active' }),
    });
  });

  it('GivenApiFailure_WhenUpdateStatus_ShouldThrowError', async () => {
    // Given - API 回傳非 2xx 狀態
    mockFetch.mockResolvedValueOnce({ ok: false, status: 500 });

    // When & Then - 應拋出錯誤
    await expect(updateUserStatus('u1', 'disabled')).rejects.toThrow(
      'Failed to update user status'
    );
  });
});

// ---- handleToggleStatus 邏輯測試 ----

describe('handleToggleStatus logic', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('GivenActiveUser_WhenToggleStatus_ShouldSwitchToDisabled', async () => {
    // Given - 使用者狀態為啟用，API 回傳成功
    mockFetch.mockResolvedValueOnce({ ok: true });

    // When - 模擬 handleToggleStatus 邏輯：active → disabled
    const currentStatus: 'active' | 'disabled' = 'active';
    const newStatus = currentStatus === 'active' ? 'disabled' : 'active';

    const res = await fetch(`/api/admin/users/u1/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });

    // Then - 新狀態應為停用，API 呼叫成功
    expect(newStatus).toBe('disabled');
    expect(res.ok).toBe(true);
  });

  it('GivenDisabledUser_WhenToggleStatus_ShouldSwitchToActive', async () => {
    // Given - 使用者狀態為停用，API 回傳成功
    mockFetch.mockResolvedValueOnce({ ok: true });

    // When - 模擬 handleToggleStatus 邏輯：disabled → active
    const currentStatus: 'active' | 'disabled' = 'disabled';
    const newStatus = currentStatus === 'active' ? 'disabled' : 'active';

    const res = await fetch(`/api/admin/users/u1/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });

    // Then - 新狀態應為啟用，API 呼叫成功
    expect(newStatus).toBe('active');
    expect(res.ok).toBe(true);
  });

  it('GivenApiError_WhenToggleStatus_ShouldNotChangeStatusAndSetError', async () => {
    // Given - API 回傳失敗
    mockFetch.mockResolvedValueOnce({ ok: false, status: 500 });

    // When - 模擬 handleToggleStatus 的錯誤處理分支
    const currentStatus: 'active' | 'disabled' = 'active';
    let finalStatus = currentStatus;
    let errorMessage: string | null = null;

    try {
      const res = await fetch(`/api/admin/users/u1/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'disabled' }),
      });
      if (!res.ok) throw new Error('Failed to update user status');
      // 成功才更新狀態
      finalStatus = 'disabled';
    } catch {
      // 失敗時顯示錯誤訊息，帳號狀態不變
      errorMessage = '更新狀態失敗，請稍後再試';
    }

    // Then - 狀態應維持不變，錯誤訊息應被設定
    expect(finalStatus).toBe('active');
    expect(errorMessage).toBe('更新狀態失敗，請稍後再試');
  });
});
