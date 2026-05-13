import React, { useEffect, useState } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'disabled';
  createdAt: string;
}

// 呼叫使用者列表 API，支援 email 關鍵字篩選
async function fetchUsers(email?: string): Promise<User[]> {
  const url = email
    ? `/api/admin/users?email=${encodeURIComponent(email)}`
    : '/api/admin/users';
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch users');
  }
  return res.json();
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [searchEmail, setSearchEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // 當搜尋關鍵字變更時重新取得列表
  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchUsers(searchEmail || undefined)
      .then((data) => setUsers(data))
      .catch(() => setError('載入使用者列表失敗'))
      .finally(() => setLoading(false));
  }, [searchEmail]);

  return (
    <div>
      <h1>使用者管理</h1>
      <input
        type="text"
        placeholder="搜尋 email"
        value={searchEmail}
        onChange={(e) => setSearchEmail(e.target.value)}
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
