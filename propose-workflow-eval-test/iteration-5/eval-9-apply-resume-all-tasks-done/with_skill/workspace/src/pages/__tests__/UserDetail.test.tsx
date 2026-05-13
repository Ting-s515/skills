/**
 * UserDetail 單元測試（BDD 原則）
 *
 * 測試範圍：handleToggleStatus 的狀態切換邏輯、API 呼叫、成功/失敗處理
 * 不涵蓋：UI 渲染結果、DOM 結構
 */

import React from 'react';
import { render, act, waitFor, fireEvent } from '@testing-library/react';
import UserDetail from '../UserDetail';

// Mock 全域 fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('UserDetail', () => {
  const mockUser = {
    id: '1',
    name: '王小明',
    email: 'wang@test.com',
    status: 'active' as const,
    createdAt: '2024-01-01',
    orderCount: 5,
  };

  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('fetchUserDetail - 使用者詳情載入', () => {
    it('GivenUserId_WhenComponentMounts_ShouldFetchUserDetail', async () => {
      // Given - 提供有效的 userId
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUser,
      });

      // When - 元件掛載，帶入 userId
      await act(async () => {
        render(<UserDetail userId="1" />);
      });

      // Then - 應呼叫正確的 GET API 路徑
      expect(mockFetch).toHaveBeenCalledWith('/api/admin/users/1');
    });

    it('GivenApiReturnsUser_WhenFetch_ShouldDisplayUserInfo', async () => {
      // Given - API 回傳使用者詳情
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUser,
      });

      // When - 元件掛載並等待資料載入
      let getByText: (text: string) => HTMLElement;
      await act(async () => {
        const rendered = render(<UserDetail userId="1" />);
        getByText = rendered.getByText;
      });

      // Then - 應顯示使用者姓名、email、建立時間、訂單數量
      await waitFor(() => {
        expect(getByText('姓名：王小明')).toBeTruthy();
        expect(getByText('Email：wang@test.com')).toBeTruthy();
        expect(getByText('訂單數量：5')).toBeTruthy();
      });
    });
  });

  describe('handleToggleStatus - 停用/啟用帳號邏輯', () => {
    it('GivenUserIsActive_WhenToggleStatus_ShouldCallPatchWithDisabled', async () => {
      // Given - 使用者狀態為啟用（active）
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockUser }) // fetchUserDetail
        .mockResolvedValueOnce({ ok: true, json: async () => ({}) }); // handleToggleStatus

      let getByText: (text: string | RegExp) => HTMLElement;
      await act(async () => {
        const rendered = render(<UserDetail userId="1" />);
        getByText = rendered.getByText;
      });

      await waitFor(() => {
        expect(getByText('停用')).toBeTruthy();
      });

      // When - 管理員點擊「停用」按鈕
      await act(async () => {
        fireEvent.click(getByText('停用'));
      });

      // Then - 應以 PATCH 呼叫狀態切換 API，傳入 disabled
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

    it('GivenUserIsDisabled_WhenToggleStatus_ShouldCallPatchWithActive', async () => {
      // Given - 使用者狀態為停用（disabled）
      const disabledUser = { ...mockUser, status: 'disabled' as const };
      mockFetch
        .mockResolvedValueOnce({ json: async () => disabledUser }) // fetchUserDetail
        .mockResolvedValueOnce({ ok: true, json: async () => ({}) }); // handleToggleStatus

      let getByText: (text: string | RegExp) => HTMLElement;
      await act(async () => {
        const rendered = render(<UserDetail userId="1" />);
        getByText = rendered.getByText;
      });

      await waitFor(() => {
        expect(getByText('啟用')).toBeTruthy();
      });

      // When - 管理員點擊「啟用」按鈕
      await act(async () => {
        fireEvent.click(getByText('啟用'));
      });

      // Then - 應以 PATCH 呼叫 API，傳入 active
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/admin/users/1/status',
          expect.objectContaining({
            method: 'PATCH',
            body: JSON.stringify({ status: 'active' }),
          })
        );
      });
    });

    it('GivenToggleSuccess_WhenApiReturnsOk_ShouldUpdateUserStatus', async () => {
      // Given - API 回傳 ok: true
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockUser }) // fetchUserDetail
        .mockResolvedValueOnce({ ok: true }); // handleToggleStatus 成功

      let getByText: (text: string | RegExp) => HTMLElement;
      await act(async () => {
        const rendered = render(<UserDetail userId="1" />);
        getByText = rendered.getByText;
      });

      await waitFor(() => expect(getByText('停用')).toBeTruthy());

      // When - 點擊停用按鈕，API 成功
      await act(async () => {
        fireEvent.click(getByText('停用'));
      });

      // Then - 畫面狀態應更新為 disabled（按鈕文字變為「啟用」）
      await waitFor(() => {
        expect(getByText('啟用')).toBeTruthy();
      });
    });

    it('GivenToggleFailed_WhenApiReturnsError_ShouldShowErrorMessage', async () => {
      // Given - API 回傳 ok: false（失敗）
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockUser }) // fetchUserDetail
        .mockResolvedValueOnce({ ok: false }); // handleToggleStatus 失敗

      let getByText: (text: string | RegExp) => HTMLElement;
      await act(async () => {
        const rendered = render(<UserDetail userId="1" />);
        getByText = rendered.getByText;
      });

      await waitFor(() => expect(getByText('停用')).toBeTruthy());

      // When - 點擊停用按鈕，API 失敗
      await act(async () => {
        fireEvent.click(getByText('停用'));
      });

      // Then - 應顯示錯誤訊息，帳號狀態不變（仍為 active，按鈕仍為「停用」）
      await waitFor(() => {
        expect(getByText('操作失敗，請稍後再試')).toBeTruthy();
        expect(getByText('停用')).toBeTruthy();
      });
    });

    it('GivenToggleFailed_WhenApiReturnsError_ShouldNotChangeUserStatus', async () => {
      // Given - 使用者狀態為 active，API 回傳失敗
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockUser })
        .mockResolvedValueOnce({ ok: false });

      let container: HTMLElement;
      await act(async () => {
        const rendered = render(<UserDetail userId="1" />);
        container = rendered.container;
      });

      await waitFor(() => {
        // 狀態顯示為啟用
        expect(container.textContent).toContain('啟用');
      });

      // When - 點擊停用按鈕，操作失敗
      await act(async () => {
        const button = container.querySelector('button');
        if (button) fireEvent.click(button);
      });

      // Then - 狀態文字不應變更為停用（仍應顯示啟用）
      await waitFor(() => {
        const statusTexts = Array.from(container.querySelectorAll('p')).map(
          (p) => p.textContent
        );
        expect(statusTexts.some((t) => t?.includes('啟用'))).toBe(true);
      });
    });
  });

  describe('handleToggleStatus - 邊界情況', () => {
    it('GivenUserIsNull_WhenToggleStatus_ShouldNotCallApi', async () => {
      // Given - user 狀態為 null（尚未載入）
      // fetchUserDetail 尚未完成，user 為 null
      mockFetch.mockResolvedValueOnce({
        json: () => new Promise(() => {}), // 永不 resolve，模擬 loading 中
      });

      render(<UserDetail userId="1" />);

      // When - 此時 user 為 null，handleToggleStatus 應提前 return
      // 由於處於 loading 狀態，按鈕不可見，驗證 fetch 只被呼叫一次（fetchUserDetail）
      await waitFor(() => {
        // 只有 fetchUserDetail 的呼叫，不應有 status PATCH
        expect(mockFetch).toHaveBeenCalledTimes(1);
        expect(mockFetch).not.toHaveBeenCalledWith(
          expect.stringContaining('/status'),
          expect.anything()
        );
      });
    });
  });
});
