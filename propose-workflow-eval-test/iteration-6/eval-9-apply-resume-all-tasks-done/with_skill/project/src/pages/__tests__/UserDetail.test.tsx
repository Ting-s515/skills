/**
 * UserDetail BDD 單元測試
 *
 * 對應 Gherkin Scenario：
 * - 管理員查看使用者詳情
 * - 管理員停用使用者帳號
 * - 停用操作失敗
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import UserDetail from '../UserDetail';

// Mock fetch API
const mockFetch = jest.fn();
global.fetch = mockFetch;

const mockUser = {
  id: '1',
  name: '王小明',
  email: 'ming@example.com',
  status: 'active' as const,
  createdAt: '2024-01-01',
  orderCount: 5,
};

const mockDisabledUser = {
  ...mockUser,
  status: 'disabled' as const,
};

describe('UserDetail', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe('管理員查看使用者詳情', () => {
    it('GivenUserOnListPage_WhenClickUser_ShouldDisplayNameEmailCreatedAtOrderCount', async () => {
      // Given - API 回傳使用者詳情
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUser,
      });

      // When - 渲染 UserDetail 元件
      render(<UserDetail userId="1" />);

      // Then - 應顯示姓名、email、建立時間、訂單數量
      await waitFor(() => {
        expect(screen.getByText('姓名：王小明')).toBeInTheDocument();
        expect(screen.getByText('Email：ming@example.com')).toBeInTheDocument();
        expect(screen.getByText('建立時間：2024-01-01')).toBeInTheDocument();
        expect(screen.getByText('訂單數量：5')).toBeInTheDocument();
      });
    });

    it('GivenUserDetailLoading_WhenFetching_ShouldShowLoadingIndicator', () => {
      // Given - API 尚未回傳
      mockFetch.mockReturnValueOnce(new Promise(() => {}));

      // When - 渲染元件
      render(<UserDetail userId="1" />);

      // Then - 顯示載入中
      expect(screen.getByText('載入中...')).toBeInTheDocument();
    });

    it('GivenUserDetail_WhenFetched_ShouldCallCorrectApiEndpoint', async () => {
      // Given - API 準備回傳資料
      mockFetch.mockResolvedValueOnce({ json: async () => mockUser });

      // When - 渲染帶有 userId 的元件
      render(<UserDetail userId="42" />);

      // Then - 應呼叫正確的 API 端點
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/42');
      });
    });
  });

  describe('管理員停用使用者帳號', () => {
    it('GivenUserStatusActive_WhenClickDisableButton_ShouldUpdateStatusToDisabled', async () => {
      // Given - 使用者狀態為啟用
      mockFetch.mockResolvedValueOnce({ json: async () => mockUser });
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByText('狀態：啟用'));

      // When - 點擊停用按鈕
      const disableBtn = screen.getByRole('button', { name: '停用' });
      fireEvent.click(disableBtn);

      // Then - 畫面狀態更新為停用
      await waitFor(() => {
        expect(screen.getByText('狀態：停用')).toBeInTheDocument();
      });
    });

    it('GivenUserStatusActive_WhenClickDisableButton_ShouldCallPatchApiWithDisabledStatus', async () => {
      // Given - 使用者狀態為啟用
      mockFetch.mockResolvedValueOnce({ json: async () => mockUser });
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByText('狀態：啟用'));

      // When - 點擊停用按鈕
      fireEvent.click(screen.getByRole('button', { name: '停用' }));

      // Then - 應以正確參數呼叫 PATCH API
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/admin/users/1/status',
          expect.objectContaining({
            method: 'PATCH',
            body: JSON.stringify({ status: 'disabled' }),
          })
        );
      });
    });

    it('GivenUserStatusDisabled_WhenClickEnableButton_ShouldUpdateStatusToActive', async () => {
      // Given - 使用者狀態為停用
      mockFetch.mockResolvedValueOnce({ json: async () => mockDisabledUser });
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByText('狀態：停用'));

      // When - 點擊啟用按鈕
      const enableBtn = screen.getByRole('button', { name: '啟用' });
      fireEvent.click(enableBtn);

      // Then - 畫面狀態更新為啟用
      await waitFor(() => {
        expect(screen.getByText('狀態：啟用')).toBeInTheDocument();
      });
    });
  });

  describe('停用操作失敗', () => {
    it('GivenAdminClicksDisableButton_WhenApiReturnsError_ShouldShowErrorMessage', async () => {
      // Given - 詳情 API 成功，但狀態變更 API 失敗
      mockFetch.mockResolvedValueOnce({ json: async () => mockUser });
      mockFetch.mockResolvedValueOnce({ ok: false });

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByText('狀態：啟用'));

      // When - 點擊停用按鈕，API 回傳錯誤
      fireEvent.click(screen.getByRole('button', { name: '停用' }));

      // Then - 顯示錯誤訊息
      await waitFor(() => {
        expect(screen.getByText('操作失敗，請稍後再試')).toBeInTheDocument();
      });
    });

    it('GivenAdminClicksDisableButton_WhenApiReturnsError_ShouldNotChangeStatus', async () => {
      // Given - 狀態變更 API 失敗
      mockFetch.mockResolvedValueOnce({ json: async () => mockUser });
      mockFetch.mockResolvedValueOnce({ ok: false });

      render(<UserDetail userId="1" />);
      await waitFor(() => screen.getByText('狀態：啟用'));

      // When - 點擊停用按鈕
      fireEvent.click(screen.getByRole('button', { name: '停用' }));

      // Then - 帳號狀態不變（仍為啟用）
      await waitFor(() => {
        expect(screen.getByText('狀態：啟用')).toBeInTheDocument();
      });
    });
  });
});
