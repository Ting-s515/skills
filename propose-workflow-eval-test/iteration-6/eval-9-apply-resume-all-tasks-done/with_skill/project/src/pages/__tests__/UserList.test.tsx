/**
 * UserList BDD 單元測試
 *
 * 對應 Gherkin Scenario：
 * - 管理員查看使用者列表
 * - 管理員依 email 搜尋使用者
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import UserList from '../UserList';

// Mock fetch API
const mockFetch = jest.fn();
global.fetch = mockFetch;

const mockUsers = [
  {
    id: '1',
    name: '王小明',
    email: 'ming@example.com',
    status: 'active' as const,
    createdAt: '2024-01-01',
  },
  {
    id: '2',
    name: '李小華',
    email: 'hua@example.com',
    status: 'disabled' as const,
    createdAt: '2024-02-01',
  },
];

describe('UserList', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe('管理員查看使用者列表', () => {
    it('GivenAdminLoggedIn_WhenEnterUserPage_ShouldFetchAndDisplayAllUsers', async () => {
      // Given - API 回傳使用者清單
      mockFetch.mockResolvedValueOnce({
        json: async () => mockUsers,
      });

      // When - 渲染 UserList 頁面
      render(<UserList />);

      // Then - 應顯示所有使用者列表，包含姓名、email、狀態、建立時間
      await waitFor(() => {
        expect(screen.getByText('王小明')).toBeInTheDocument();
        expect(screen.getByText('ming@example.com')).toBeInTheDocument();
        expect(screen.getByText('啟用')).toBeInTheDocument();
        expect(screen.getByText('2024-01-01')).toBeInTheDocument();

        expect(screen.getByText('李小華')).toBeInTheDocument();
        expect(screen.getByText('hua@example.com')).toBeInTheDocument();
        expect(screen.getByText('停用')).toBeInTheDocument();
      });
    });

    it('GivenAdminLoggedIn_WhenEnterUserPage_ShouldCallApiWithoutParams', async () => {
      // Given - 進入頁面，尚未輸入關鍵字
      mockFetch.mockResolvedValueOnce({ json: async () => [] });

      // When - 渲染元件
      render(<UserList />);

      // Then - 應呼叫不帶參數的 API
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/admin/users');
      });
    });

    it('GivenApiLoading_WhenEnterUserPage_ShouldShowLoadingIndicator', () => {
      // Given - API 尚未回傳（pending promise）
      mockFetch.mockReturnValueOnce(new Promise(() => {}));

      // When - 渲染元件
      render(<UserList />);

      // Then - 應顯示載入中
      expect(screen.getByText('載入中...')).toBeInTheDocument();
    });
  });

  describe('管理員依 email 搜尋使用者', () => {
    it('GivenUserOnListPage_WhenEnterEmailKeyword_ShouldCallApiWithEmailParam', async () => {
      // Given - 初始載入
      mockFetch.mockResolvedValueOnce({ json: async () => mockUsers });
      render(<UserList />);
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));

      // 準備搜尋結果
      const filtered = [mockUsers[0]];
      mockFetch.mockResolvedValueOnce({ json: async () => filtered });

      // When - 輸入 email 關鍵字
      const searchInput = screen.getByPlaceholderText('搜尋 email');
      fireEvent.change(searchInput, { target: { value: 'ming' } });

      // Then - 應呼叫帶 email 參數的 API
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/admin/users?email=ming'
        );
      });
    });

    it('GivenUserOnListPage_WhenEnterEmailKeyword_ShouldDisplayOnlyMatchingUsers', async () => {
      // Given - 初始載入
      mockFetch.mockResolvedValueOnce({ json: async () => mockUsers });
      render(<UserList />);
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));

      // 搜尋 API 只回傳符合的使用者
      const filtered = [mockUsers[0]];
      mockFetch.mockResolvedValueOnce({ json: async () => filtered });

      // When - 輸入關鍵字
      const searchInput = screen.getByPlaceholderText('搜尋 email');
      fireEvent.change(searchInput, { target: { value: 'ming' } });

      // Then - 只顯示符合的使用者
      await waitFor(() => {
        expect(screen.getByText('王小明')).toBeInTheDocument();
        expect(screen.queryByText('李小華')).not.toBeInTheDocument();
      });
    });

    it('GivenUserTypedKeyword_WhenClearKeyword_ShouldCallApiWithoutParams', async () => {
      // Given - 先搜尋後清空
      mockFetch.mockResolvedValue({ json: async () => mockUsers });
      render(<UserList />);
      const searchInput = screen.getByPlaceholderText('搜尋 email');
      fireEvent.change(searchInput, { target: { value: 'ming' } });
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));

      mockFetch.mockResolvedValueOnce({ json: async () => mockUsers });

      // When - 清空關鍵字
      fireEvent.change(searchInput, { target: { value: '' } });

      // Then - 應重新呼叫不帶參數的 API
      await waitFor(() => {
        const calls = mockFetch.mock.calls;
        const lastCall = calls[calls.length - 1];
        expect(lastCall[0]).toBe('/api/admin/users');
      });
    });
  });
});
