import React, { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [emailKeyword, setEmailKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 根據是否有 email 關鍵字決定呼叫哪個 API
  const fetchUsers = async (keyword: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = keyword
        ? `/api/admin/users?email=${encodeURIComponent(keyword)}`
        : '/api/admin/users';
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('取得使用者列表失敗');
      }
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '發生未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  // 初次載入取得全部使用者
  useEffect(() => {
    fetchUsers('');
  }, []);

  // email 搜尋欄位變更時重新篩選
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const keyword = e.target.value;
    setEmailKeyword(keyword);
    fetchUsers(keyword);
  };

  const handleUserClick = (userId: string) => {
    window.location.href = `/admin/users/${userId}`;
  };

  return (
    <div>
      <h1>使用者管理</h1>
      <input
        type="text"
        placeholder="輸入 email 搜尋"
        value={emailKeyword}
        onChange={handleSearchChange}
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
            <tr
              key={user.id}
              onClick={() => handleUserClick(user.id)}
              style={{ cursor: 'pointer' }}
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
