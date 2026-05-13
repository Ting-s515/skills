import React, { useState, useEffect } from 'react';

// 使用者資料結構
interface User {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

interface FetchUsersResponse {
  users: User[];
}

// 呼叫 GET /api/admin/users，可帶 email 過濾參數
async function fetchUsers(emailKeyword?: string): Promise<User[]> {
  const url = emailKeyword
    ? `/api/admin/users?email=${encodeURIComponent(emailKeyword)}`
    : '/api/admin/users';
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  const data: FetchUsersResponse = await response.json();
  return data.users;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [emailKeyword, setEmailKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 載入使用者清單，有關鍵字時進行 email 篩選
  const loadUsers = async (keyword: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchUsers(keyword || undefined);
      setUsers(result);
    } catch (err) {
      setError('無法載入使用者列表，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  // 頁面初次載入時取得所有使用者
  useEffect(() => {
    loadUsers('');
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmailKeyword(value);
    // 每次輸入改變都重新查詢
    loadUsers(value);
  };

  return (
    <div>
      <h1>使用者管理</h1>
      <input
        type="text"
        placeholder="搜尋 email"
        value={emailKeyword}
        onChange={handleSearchChange}
      />
      {loading && <p>載入中...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>姓名</th>
              <th>Email</th>
              <th>狀態</th>
              <th>建立時間</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.status === 'active' ? '啟用' : '停用'}</td>
                <td>{user.createdAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default UserList;
export { fetchUsers };
export type { User };
