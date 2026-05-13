import React, { useEffect, useState } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'disabled';
  createdAt: string;
}

// 呼叫後端 API 取得使用者列表，支援 email 關鍵字篩選
async function fetchUsers(emailKeyword?: string): Promise<User[]> {
  const url = emailKeyword
    ? `/api/admin/users?email=${encodeURIComponent(emailKeyword)}`
    : '/api/admin/users';
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [emailKeyword, setEmailKeyword] = useState('');
  const [error, setError] = useState<string | null>(null);

  // 每次 emailKeyword 變更時重新取得列表
  useEffect(() => {
    setError(null);
    fetchUsers(emailKeyword || undefined)
      .then(setUsers)
      .catch(() => setError('載入使用者失敗'));
  }, [emailKeyword]);

  return (
    <div>
      <h1>使用者管理</h1>
      <input
        type="text"
        placeholder="搜尋 email"
        value={emailKeyword}
        onChange={(e) => setEmailKeyword(e.target.value)}
        aria-label="搜尋 email"
      />
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
            <tr key={user.id}>
              <td>
                <a href={`/admin/users/${user.id}`}>{user.name}</a>
              </td>
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
