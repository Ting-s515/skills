import React, { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'disabled';
  createdAt: string;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [emailKeyword, setEmailKeyword] = useState('');
  const [loading, setLoading] = useState(false);

  // 依據是否有 email 關鍵字決定呼叫的 API 路徑
  const fetchUsers = async (keyword: string) => {
    setLoading(true);
    const url = keyword
      ? `/api/admin/users?email=${encodeURIComponent(keyword)}`
      : '/api/admin/users';
    const res = await fetch(url);
    const data = await res.json();
    setUsers(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchUsers(emailKeyword);
  }, [emailKeyword]);

  return (
    <div>
      <h1>使用者管理</h1>
      <input
        type="text"
        placeholder="搜尋 email"
        value={emailKeyword}
        onChange={(e) => setEmailKeyword(e.target.value)}
      />
      {loading ? (
        <p>載入中...</p>
      ) : (
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
