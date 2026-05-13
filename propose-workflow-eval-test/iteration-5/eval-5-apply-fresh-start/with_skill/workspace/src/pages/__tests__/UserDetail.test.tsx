/**
 * UserDetail 服務函式 BDD 單元測試
 * 對照 02-gherkin.md 驗收條件：
 *   Scenario: 管理員查看使用者詳情
 *   Scenario: 管理員停用使用者帳號
 *   Scenario: 停用操作失敗
 */

import { fetchUserDetail, updateUserStatus } from '../UserDetail';
import type { UserDetail } from '../UserDetail';

// Mock 全域 fetch
global.fetch = jest.fn();

const mockUserDetail: UserDetail = {
  id: '1',
  name: '王小明',
  email: 'ming@example.com',
  status: 'active',
  createdAt: '2024-01-01',
  orderCount: 5,
};

describe('fetchUserDetail', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('管理員查看使用者詳情', () => {
    it('GivenValidUserId_WhenFetchUserDetail_ShouldReturnUserWithAllFields', async () => {
      // Given - userId 有效
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockUserDetail,
      });

      // When - 呼叫 fetchUserDetail
      const result = await fetchUserDetail('1');

      // Then - 應呼叫正確 URL，並回傳含姓名、email、建立時間、訂單數量的詳情
      expect(fetch).toHaveBeenCalledWith('/api/admin/users/1');
      expect(result.name).toBe('王小明');
      expect(result.email).toBe('ming@example.com');
      expect(result.createdAt).toBe('2024-01-01');
      expect(result.orderCount).toBe(5);
    });

    it('GivenApiReturnsError_WhenFetchUserDetail_ShouldThrowError', async () => {
      // Given - API 回傳非 2xx（例如 404 找不到使用者）
      (fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
      });

      // When & Then - 應拋出錯誤
      await expect(fetchUserDetail('999')).rejects.toThrow(
        'Failed to fetch user detail'
      );
    });
  });
});

describe('updateUserStatus', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('管理員停用使用者帳號', () => {
    it('GivenActiveUser_WhenUpdateStatusToInactive_ShouldCallPatchWithInactiveStatus', async () => {
      // Given - 使用者目前為啟用狀態，管理員要停用
      (fetch as jest.Mock).mockResolvedValue({ ok: true });

      // When - 呼叫 updateUserStatus 設為 inactive
      await updateUserStatus('1', 'inactive');

      // Then - 應以 PATCH 呼叫正確 URL，並傳送 inactive 狀態
      expect(fetch).toHaveBeenCalledWith('/api/admin/users/1/status', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'inactive' }),
      });
    });

    it('GivenInactiveUser_WhenUpdateStatusToActive_ShouldCallPatchWithActiveStatus', async () => {
      // Given - 使用者目前為停用狀態，管理員要啟用
      (fetch as jest.Mock).mockResolvedValue({ ok: true });

      // When - 呼叫 updateUserStatus 設為 active
      await updateUserStatus('1', 'active');

      // Then - 應傳送 active 狀態
      expect(fetch).toHaveBeenCalledWith('/api/admin/users/1/status', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'active' }),
      });
    });
  });

  describe('停用操作失敗', () => {
    it('GivenApiReturnsError_WhenUpdateUserStatus_ShouldThrowError', async () => {
      // Given - API 回傳錯誤（例如伺服器異常）
      (fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
      });

      // When & Then - 應拋出錯誤，讓呼叫方顯示錯誤訊息，帳號狀態不變
      await expect(updateUserStatus('1', 'inactive')).rejects.toThrow(
        'Failed to update user status'
      );
    });

    it('GivenNetworkFailure_WhenUpdateUserStatus_ShouldPropagateError', async () => {
      // Given - 網路連線失敗
      (fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      // When & Then - 應向上拋出網路錯誤
      await expect(updateUserStatus('1', 'inactive')).rejects.toThrow(
        'Network error'
      );
    });
  });
});
