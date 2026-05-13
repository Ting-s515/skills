import React, { useEffect, useState } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'disabled';
  createdAt: string;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  // 搜尋關鍵字，用於依 email 篩選使用者
  const [emailKeyword, setEmailKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 依照搜尋關鍵字決定呼叫哪個 API endpoint
  const fetchUsers = async (keyword: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = keyword
        ? `/api/admin/users?email=${encodeURIComponent(keyword)}`
        : '/api/admin/users';
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error('Failed to fetch users');
      }
      const data: User[] = await res.json();
      setUsers(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 初始載入全部使用者
  useEffect(() => {
    fetchUsers('');
  }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmailKeyword(value);
    fetchUsers(value);
  };

  return (
    <div>
      <h1>使用者管理</h1>
      <input
        type="text"
        placeholder="搜尋 email"
        value={emailKeyword}
        onChange={handleSearch}
      />
      {loading && <p>載入中...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
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
    </div>
  );
};

export default UserList;
