import React, { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'disabled';
  createdAt: string;
}

interface UserListResponse {
  users: User[];
}

// 呼叫使用者列表 API，支援依 email 關鍵字篩選
async function fetchUsers(emailKeyword?: string): Promise<User[]> {
  const url = emailKeyword
    ? `/api/admin/users?email=${encodeURIComponent(emailKeyword)}`
    : '/api/admin/users';
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  const data: UserListResponse = await response.json();
  return data.users;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [emailKeyword, setEmailKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 初始載入全部使用者
  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async (keyword?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchUsers(keyword);
      setUsers(data);
    } catch {
      setError('載入使用者列表失敗');
    } finally {
      setLoading(false);
    }
  };

  // 搜尋框變更時觸發 API 篩選
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmailKeyword(value);
    loadUsers(value || undefined);
  };

  const handleUserClick = (userId: string) => {
    window.location.href = `/admin/users/${userId}`;
  };

  return (
    <div>
      <h1>使用者管理</h1>
      <input
        type="text"
        placeholder="搜尋 email"
        value={emailKeyword}
        onChange={handleSearchChange}
        data-testid="email-search"
      />
      {loading && <p>載入中...</p>}
      {error && <p role="alert">{error}</p>}
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
            <tr
              key={user.id}
              onClick={() => handleUserClick(user.id)}
              style={{ cursor: 'pointer' }}
              data-testid={`user-row-${user.id}`}
            >
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>{user.status === 'active' ? '啟用' : '停用'}</td>
              <td>{user.createdAt}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserList;
