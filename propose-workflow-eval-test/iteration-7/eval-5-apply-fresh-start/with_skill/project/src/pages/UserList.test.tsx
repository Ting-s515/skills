/**
 * UserList 頁面 BDD 單元測試
 *
 * 驗收條件來源：docs/propose/user-management/02-gherkin.md
 * 涵蓋：管理員查看使用者列表、依 email 搜尋使用者
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import UserList from './UserList';

// Mock 全域 fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock window.location.href 導航
const mockLocation = { href: '' };
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

const mockUsers = [
  {
    id: '1',
    name: '王小明',
    email: 'wang@example.com',
    status: 'active' as const,
    createdAt: '2024-01-01',
  },
  {
    id: '2',
    name: '李小花',
    email: 'li@example.com',
    status: 'disabled' as const,
    createdAt: '2024-02-01',
  },
];

describe('UserList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocation.href = '';
  });

  describe('管理員查看使用者列表', () => {
    it('GivenAdminLoggedIn_WhenEnterUserListPage_ShouldDisplayAllUsersWithColumns', async () => {
      // Given - API 回傳使用者列表
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ users: mockUsers }),
      });

      // When - 管理員進入使用者管理頁面
      render(<UserList />);

      // Then - 等待 API 回應後，顯示所有使用者列表含姓名、email、狀態、建立時間
      await waitFor(() => {
        expect(screen.getByText('王小明')).toBeInTheDocument();
        expect(screen.getByText('wang@example.com')).toBeInTheDocument();
        expect(screen.getByText('啟用')).toBeInTheDocument();
        expect(screen.getByText('2024-01-01')).toBeInTheDocument();

        expect(screen.getByText('李小花')).toBeInTheDocument();
        expect(screen.getByText('li@example.com')).toBeInTheDocument();
        expect(screen.getByText('停用')).toBeInTheDocument();
        expect(screen.getByText('2024-02-01')).toBeInTheDocument();
      });

      // 確認初始呼叫無 query param
      expect(mockFetch).toHaveBeenCalledWith('/api/admin/users');
    });

    it('GivenApiLoading_WhenEnterUserListPage_ShouldShowLoadingIndicator', () => {
      // Given - API 尚未回應（pending promise）
      mockFetch.mockReturnValueOnce(new Promise(() => {}));

      // When - 進入頁面
      render(<UserList />);

      // Then - 顯示載入中提示
      expect(screen.getByText('載入中...')).toBeInTheDocument();
    });
  });

  describe('管理員依 email 搜尋使用者', () => {
    it('GivenUserListLoaded_WhenInputEmailKeyword_ShouldCallFilteredApiAndShowResults', async () => {
      // Given - 初始載入完成
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ users: mockUsers }),
      });
      render(<UserList />);
      await waitFor(() => expect(screen.getByText('王小明')).toBeInTheDocument());

      // 搜尋結果只回傳一個使用者
      const filteredUsers = [mockUsers[0]];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ users: filteredUsers }),
      });

      // When - 在搜尋框輸入 email 關鍵字
      const searchInput = screen.getByTestId('email-search');
      fireEvent.change(searchInput, { target: { value: 'wang' } });

      // Then - 呼叫帶 query param 的 API，並只顯示符合的使用者
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          '/api/admin/users?email=wang'
        );
        expect(screen.getByText('王小明')).toBeInTheDocument();
        expect(screen.queryByText('李小花')).not.toBeInTheDocument();
      });
    });

    it('GivenKeywordEntered_WhenClearSearchInput_ShouldCallApiWithoutKeyword', async () => {
      // Given - 已有搜尋關鍵字並載入完成
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ users: [mockUsers[0]] }),
      });
      render(<UserList />);
      await waitFor(() => expect(screen.getByText('王小明')).toBeInTheDocument());

      // 清空後回傳全部使用者
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ users: mockUsers }),
      });

      // When - 清空搜尋框
      const searchInput = screen.getByTestId('email-search');
      fireEvent.change(searchInput, { target: { value: '' } });

      // Then - 呼叫無 query param 的全量 API
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/admin/users');
      });
    });
  });

  describe('API 失敗處理', () => {
    it('GivenApiFails_WhenEnterUserListPage_ShouldDisplayErrorMessage', async () => {
      // Given - API 回傳非 ok 狀態
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      // When - 進入使用者列表頁面
      render(<UserList />);

      // Then - 顯示錯誤訊息
      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          '載入使用者列表失敗'
        );
      });
    });
  });
});
