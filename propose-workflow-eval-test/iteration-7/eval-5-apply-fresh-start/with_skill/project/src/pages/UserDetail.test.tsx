/**
 * UserDetail 頁面 BDD 單元測試
 *
 * 驗收條件來源：docs/propose/user-management/02-gherkin.md
 * 涵蓋：查看使用者詳情、停用/啟用帳號、失敗處理
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import UserDetail from './UserDetail';

// Mock 全域 fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

const mockActiveUser = {
  id: 'u1',
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
    jest.clearAllMocks();
  });

  describe('管理員查看使用者詳情', () => {
    it('GivenAdminOnUserList_WhenClickUser_ShouldDisplayNameEmailCreatedAtOrderCount', async () => {
      // Given - 詳情 API 回傳使用者資料
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockActiveUser,
      });

      // When - 進入使用者詳情頁
      render(<UserDetail userId="u1" />);

      // Then - 顯示姓名、email、建立時間、訂單數量
      await waitFor(() => {
        expect(screen.getByTestId('user-name')).toHaveTextContent('王小明');
        expect(screen.getByTestId('user-email')).toHaveTextContent(
          'wang@example.com'
        );
        expect(screen.getByTestId('user-created-at')).toHaveTextContent(
          '2024-01-01'
        );
        expect(screen.getByTestId('user-order-count')).toHaveTextContent('5');
      });
    });
  });

  describe('管理員停用使用者帳號', () => {
    it('GivenUserStatusIsActive_WhenClickDisableButton_ShouldUpdateStatusToDisabled', async () => {
      // Given - 使用者狀態為啟用
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockActiveUser,
      });
      render(<UserDetail userId="u1" />);
      await waitFor(() =>
        expect(screen.getByTestId('user-status')).toHaveTextContent('啟用')
      );

      // PATCH API 成功回應
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      // When - 管理員點擊「停用」按鈕
      fireEvent.click(screen.getByTestId('toggle-status-btn'));

      // Then - 畫面更新狀態為停用，無錯誤訊息
      await waitFor(() => {
        expect(screen.getByTestId('user-status')).toHaveTextContent('停用');
      });
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();

      // 確認 PATCH 呼叫正確
      expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/u1/status', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'disabled' }),
      });
    });

    it('GivenUserStatusIsDisabled_WhenClickEnableButton_ShouldUpdateStatusToActive', async () => {
      // Given - 使用者狀態為停用
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDisabledUser,
      });
      render(<UserDetail userId="u1" />);
      await waitFor(() =>
        expect(screen.getByTestId('user-status')).toHaveTextContent('停用')
      );

      // PATCH API 成功回應
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      // When - 點擊「啟用」按鈕（狀態為停用時按鈕顯示「啟用」）
      expect(screen.getByTestId('toggle-status-btn')).toHaveTextContent('啟用');
      fireEvent.click(screen.getByTestId('toggle-status-btn'));

      // Then - 畫面更新狀態為啟用
      await waitFor(() => {
        expect(screen.getByTestId('user-status')).toHaveTextContent('啟用');
      });
    });
  });

  describe('停用操作失敗', () => {
    it('GivenAdminClicksDisableButton_WhenApiReturnsError_ShouldShowErrorAndKeepStatus', async () => {
      // Given - 使用者狀態為啟用，詳情載入成功
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockActiveUser,
      });
      render(<UserDetail userId="u1" />);
      await waitFor(() =>
        expect(screen.getByTestId('user-status')).toHaveTextContent('啟用')
      );

      // PATCH API 回傳錯誤
      mockFetch.mockResolvedValueOnce({ ok: false, json: async () => ({}) });

      // When - 點擊「停用」按鈕，API 回傳錯誤
      fireEvent.click(screen.getByTestId('toggle-status-btn'));

      // Then - 顯示錯誤訊息，帳號狀態不變（仍為啟用）
      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          '更新帳號狀態失敗'
        );
        expect(screen.getByTestId('user-status')).toHaveTextContent('啟用');
      });
    });
  });

  describe('詳情載入失敗', () => {
    it('GivenDetailApiFails_WhenEnterDetailPage_ShouldDisplayErrorMessage', async () => {
      // Given - 詳情 API 回傳錯誤
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      // When - 進入使用者詳情頁
      render(<UserDetail userId="u1" />);

      // Then - 顯示錯誤訊息
      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          '載入使用者詳情失敗'
        );
      });
    });
  });
});
