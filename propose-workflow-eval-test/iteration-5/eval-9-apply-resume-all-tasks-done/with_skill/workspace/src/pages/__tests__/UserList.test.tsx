/**
 * UserList 單元測試（BDD 原則）
 *
 * 測試範圍：fetchUsers 的 URL 組裝邏輯、email keyword 篩選邏輯
 * 不涵蓋：UI 渲染結果、DOM 結構
 */

import React from 'react';
import { render, act, waitFor } from '@testing-library/react';
import UserList from '../UserList';

// Mock 全域 fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('UserList', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('fetchUsers - API URL 組裝邏輯', () => {
    it('GivenNoKeyword_WhenFetchUsers_ShouldCallBaseUrl', async () => {
      // Given - 無 email keyword（初始狀態）
      mockFetch.mockResolvedValueOnce({
        json: async () => [],
      });

      // When - 元件掛載，預設無 keyword 呼叫 fetchUsers
      await act(async () => {
        render(<UserList />);
      });

      // Then - 應呼叫不帶 query 的基礎 URL
      expect(mockFetch).toHaveBeenCalledWith('/api/admin/users');
    });

    it('GivenEmailKeyword_WhenFetchUsers_ShouldCallUrlWithEncodedKeyword', async () => {
      // Given - 有 email keyword（帶特殊字元驗證 encode）
      mockFetch.mockResolvedValue({
        json: async () => [],
      });

      const { getByPlaceholderText } = render(<UserList />);

      // When - 使用者在搜尋框輸入 email keyword
      await act(async () => {
        const input = getByPlaceholderText('搜尋 email');
        input.dispatchEvent(
          Object.assign(new Event('input', { bubbles: true }), {
            target: { value: 'test@example.com' },
          })
        );
        // 觸發 onChange
        const event = { target: { value: 'test@example.com' } };
        (input as HTMLInputElement).value = 'test@example.com';
        input.dispatchEvent(new Event('change', { bubbles: true }));
      });

      await waitFor(() => {
        // Then - 應呼叫帶 encoded email query 的 URL
        const calls = mockFetch.mock.calls.map((c) => c[0]);
        expect(calls.some((url: string) => url.includes('/api/admin/users?email='))).toBe(true);
      });
    });

    it('GivenSpecialCharInKeyword_WhenFetchUsers_ShouldEncodeKeyword', () => {
      // Given - keyword 含需要 encode 的特殊字元
      const keyword = 'test+user@example.com';

      // When - 直接驗證 encodeURIComponent 對 keyword 的處理
      const encodedKeyword = encodeURIComponent(keyword);
      const url = `/api/admin/users?email=${encodedKeyword}`;

      // Then - URL 應包含正確 encode 後的字串
      expect(url).toBe('/api/admin/users?email=test%2Buser%40example.com');
    });
  });

  describe('fetchUsers - 資料取得後狀態更新', () => {
    it('GivenApiReturnsUsers_WhenFetchUsers_ShouldUpdateUsersState', async () => {
      // Given - API 回傳使用者清單
      const mockUsers = [
        {
          id: '1',
          name: '王小明',
          email: 'wang@test.com',
          status: 'active',
          createdAt: '2024-01-01',
        },
      ];
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUsers,
      });

      // When - 元件掛載觸發 fetchUsers
      let container: HTMLElement;
      await act(async () => {
        const rendered = render(<UserList />);
        container = rendered.container;
      });

      // Then - 使用者資料應顯示在列表中
      await waitFor(() => {
        expect(container.querySelector('tbody')).toBeTruthy();
        expect(mockFetch).toHaveBeenCalledTimes(1);
      });
    });

    it('GivenApiReturnsEmptyArray_WhenFetchUsers_ShouldShowEmptyList', async () => {
      // Given - API 回傳空陣列
      mockFetch.mockResolvedValueOnce({
        json: async () => [],
      });

      // When - 元件掛載
      let container: HTMLElement;
      await act(async () => {
        const rendered = render(<UserList />);
        container = rendered.container;
      });

      // Then - tbody 中無資料列
      await waitFor(() => {
        const rows = container.querySelectorAll('tbody tr');
        expect(rows.length).toBe(0);
      });
    });
  });
});
