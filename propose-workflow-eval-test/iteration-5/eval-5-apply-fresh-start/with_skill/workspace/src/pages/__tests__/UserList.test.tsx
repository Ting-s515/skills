/**
 * UserList 服務函式 BDD 單元測試
 * 對照 02-gherkin.md 驗收條件：
 *   Scenario: 管理員查看使用者列表
 *   Scenario: 管理員依 email 搜尋使用者
 */

import { fetchUsers } from '../UserList';
import type { User } from '../UserList';

// Mock 全域 fetch
global.fetch = jest.fn();

const mockUsers: User[] = [
  {
    id: '1',
    name: '王小明',
    email: 'ming@example.com',
    status: 'active',
    createdAt: '2024-01-01',
  },
  {
    id: '2',
    name: '李小華',
    email: 'hua@example.com',
    status: 'inactive',
    createdAt: '2024-02-01',
  },
];

describe('fetchUsers', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('管理員查看使用者列表', () => {
    it('GivenNoKeyword_WhenFetchUsers_ShouldCallBaseUrlAndReturnAllUsers', async () => {
      // Given - 無 email 關鍵字
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ users: mockUsers }),
      });

      // When - 呼叫 fetchUsers 不帶關鍵字
      const result = await fetchUsers();

      // Then - 應呼叫 /api/admin/users，回傳所有使用者
      expect(fetch).toHaveBeenCalledWith('/api/admin/users');
      expect(result).toHaveLength(2);
      expect(result[0].name).toBe('王小明');
      expect(result[1].name).toBe('李小華');
    });

    it('GivenEmptyKeyword_WhenFetchUsers_ShouldCallBaseUrlWithoutQueryParam', async () => {
      // Given - email 關鍵字為空字串（等同無關鍵字）
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ users: mockUsers }),
      });

      // When - 呼叫 fetchUsers 帶空字串
      const result = await fetchUsers(undefined);

      // Then - 應呼叫無參數的 URL
      expect(fetch).toHaveBeenCalledWith('/api/admin/users');
      expect(result).toHaveLength(2);
    });
  });

  describe('管理員依 email 搜尋使用者', () => {
    it('GivenEmailKeyword_WhenFetchUsers_ShouldCallUrlWithEmailParam', async () => {
      // Given - 管理員輸入 email 關鍵字 "ming"
      const filteredUsers = [mockUsers[0]];
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ users: filteredUsers }),
      });

      // When - 呼叫 fetchUsers 帶關鍵字
      const result = await fetchUsers('ming');

      // Then - 應呼叫帶 email 參數的 URL，並只回傳符合的使用者
      expect(fetch).toHaveBeenCalledWith('/api/admin/users?email=ming');
      expect(result).toHaveLength(1);
      expect(result[0].email).toBe('ming@example.com');
    });

    it('GivenSpecialCharsInKeyword_WhenFetchUsers_ShouldEncodeKeyword', async () => {
      // Given - email 關鍵字包含特殊字元（如 @）
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ users: [] }),
      });

      // When - 呼叫 fetchUsers 帶含特殊字元的關鍵字
      await fetchUsers('test@example.com');

      // Then - 應對關鍵字做 URL encode
      expect(fetch).toHaveBeenCalledWith(
        '/api/admin/users?email=test%40example.com'
      );
    });
  });

  describe('API 錯誤處理', () => {
    it('GivenApiReturnsError_WhenFetchUsers_ShouldThrowError', async () => {
      // Given - API 回傳非 2xx 狀態碼
      (fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
      });

      // When & Then - 應拋出錯誤
      await expect(fetchUsers()).rejects.toThrow('Failed to fetch users');
    });
  });
});
