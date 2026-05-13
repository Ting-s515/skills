/**
 * UserDetail 元件邏輯測試
 *
 * 測試範圍：
 * - fetchUserDetail：進入頁面時取得使用者詳情
 * - handleToggleStatus：停用/啟用帳號的狀態切換邏輯與錯誤處理
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import UserDetail from '../UserDetail';

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

const mockActiveUser = {
  id: '1',
  name: '王小明',
  email: 'wang@example.com',
  status: 'active' as const,
  createdAt: '2024-01-01',
  orderCount: 5,
};

const mockDisabledUser = {
  ...mockActiveUser,
  status: 'disabled' as const,
};

describe('UserDetail', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe('fetchUserDetail', () => {
    it('GivenUserId_WhenComponentMounts_ShouldFetchUserDetailById', async () => {
      // Given - fetch 回傳使用者詳情
      mockFetch.mockResolvedValueOnce({
        json: async () => mockActiveUser,
      } as Response);

      // When - 元件以 userId='1' 掛載
      render(<UserDetail userId="1" />);

      // Then - 應呼叫正確的 API 路徑
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/1');
      });
    });

    it('GivenApiReturnsUser_WhenComponentMounts_ShouldDisplayUserInfo', async () => {
      // Given - API 回傳完整使用者資料
      mockFetch.mockResolvedValueOnce({
        json: async () => mockActiveUser,
      } as Response);

      // When - 元件載入
      render(<UserDetail userId="1" />);

      // Then - 應顯示姓名、email、建立時間、訂單數量
      await waitFor(() => {
        expect(screen.getByText(/王小明/)).toBeInTheDocument();
        expect(screen.getByText(/wang@example.com/)).toBeInTheDocument();
        expect(screen.getByText(/2024-01-01/)).toBeInTheDocument();
        expect(screen.getByText(/5/)).toBeInTheDocument();
      });
    });
  });

  describe('handleToggleStatus', () => {
    it('GivenUserIsActive_WhenClickDisableButton_ShouldCallPatchWithDisabled', async () => {
      // Given - 使用者狀態為啟用，fetch 第一次回傳詳情、第二次回傳成功
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockActiveUser } as Response)
        .mockResolvedValueOnce({ ok: true } as Response);

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByText('停用'));

      // When - 管理員點擊「停用」按鈕
      fireEvent.click(screen.getByRole('button', { name: '停用' }));

      // Then - 應呼叫 PATCH API 並帶入 disabled 狀態
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/1/status', {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'disabled' }),
        });
      });
    });

    it('GivenUserIsActive_WhenDisableSuccess_ShouldUpdateStatusOnScreen', async () => {
      // Given - PATCH 成功
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockActiveUser } as Response)
        .mockResolvedValueOnce({ ok: true } as Response);

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByRole('button', { name: '停用' }));

      // When - 點擊停用按鈕
      fireEvent.click(screen.getByRole('button', { name: '停用' }));

      // Then - 按鈕應切換為「啟用」，畫面狀態更新
      await waitFor(() => {
        expect(screen.getByRole('button', { name: '啟用' })).toBeInTheDocument();
      });
    });

    it('GivenUserIsDisabled_WhenClickEnableButton_ShouldCallPatchWithActive', async () => {
      // Given - 使用者狀態為停用
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockDisabledUser } as Response)
        .mockResolvedValueOnce({ ok: true } as Response);

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByRole('button', { name: '啟用' }));

      // When - 管理員點擊「啟用」按鈕
      fireEvent.click(screen.getByRole('button', { name: '啟用' }));

      // Then - 應呼叫 PATCH API 並帶入 active 狀態
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/1/status', {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'active' }),
        });
      });
    });

    it('GivenApiReturnsError_WhenToggleStatus_ShouldShowErrorMessageAndKeepStatus', async () => {
      // Given - PATCH 回傳失敗
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockActiveUser } as Response)
        .mockResolvedValueOnce({ ok: false } as Response);

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByRole('button', { name: '停用' }));

      // When - 點擊停用按鈕，API 回傳錯誤
      fireEvent.click(screen.getByRole('button', { name: '停用' }));

      // Then - 應顯示錯誤訊息，按鈕維持「停用」（狀態不變）
      await waitFor(() => {
        expect(screen.getByText('操作失敗，請稍後再試')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: '停用' })).toBeInTheDocument();
      });
    });
  });
});
