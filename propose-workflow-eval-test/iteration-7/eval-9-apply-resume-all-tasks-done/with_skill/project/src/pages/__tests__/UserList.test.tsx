/**
 * UserList 元件邏輯測試
 *
 * 測試範圍：fetchUsers 呼叫邏輯（API URL 組裝、使用者列表狀態更新）
 * 不測試 UI 渲染細節
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UserList from '../UserList';

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

const mockUsers = [
  { id: '1', name: '王小明', email: 'wang@example.com', status: 'active', createdAt: '2024-01-01' },
  { id: '2', name: '李小花', email: 'li@example.com', status: 'disabled', createdAt: '2024-02-01' },
];

describe('UserList', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe('fetchUsers', () => {
    it('GivenNoKeyword_WhenPageLoads_ShouldFetchAllUsers', async () => {
      // Given - fetch 回傳完整使用者清單
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUsers,
      } as Response);

      // When - 元件載入（無搜尋關鍵字）
      render(<UserList />);

      // Then - 應呼叫不帶 query 的 API
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/admin/users');
      });
    });

    it('GivenEmailKeyword_WhenUserTypesInSearch_ShouldFetchWithEmailQuery', async () => {
      // Given - 第一次載入回傳全部，第二次回傳篩選結果
      mockFetch
        .mockResolvedValueOnce({ json: async () => mockUsers } as Response)
        .mockResolvedValueOnce({
          json: async () => [mockUsers[0]],
        } as Response);

      render(<UserList />);
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));

      // When - 使用者在搜尋框輸入 email 關鍵字
      const input = screen.getByPlaceholderText('搜尋 email');
      await act(async () => {
        await userEvent.type(input, 'wang');
      });

      // Then - 應呼叫帶 email query 的 API（包含最後輸入的字母觸發的呼叫）
      await waitFor(() => {
        const calls = mockFetch.mock.calls.map((c) => c[0] as string);
        expect(calls.some((url) => url.includes('email=') && url.includes('wang'))).toBe(true);
      });
    });

    it('GivenApiReturnsUsers_WhenPageLoads_ShouldDisplayUserList', async () => {
      // Given - API 回傳兩位使用者
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUsers,
      } as Response);

      // When - 元件載入
      render(<UserList />);

      // Then - 畫面應顯示使用者姓名
      await waitFor(() => {
        expect(screen.getByText('王小明')).toBeInTheDocument();
        expect(screen.getByText('李小花')).toBeInTheDocument();
      });
    });

    it('GivenApiReturnsUsers_WhenPageLoads_ShouldShowStatusLabels', async () => {
      // Given - 使用者狀態分別為 active 與 disabled
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUsers,
      } as Response);

      // When - 元件載入
      render(<UserList />);

      // Then - 應顯示對應的中文狀態標籤
      await waitFor(() => {
        expect(screen.getByText('啟用')).toBeInTheDocument();
        expect(screen.getByText('停用')).toBeInTheDocument();
      });
    });
  });
});
