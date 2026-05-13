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
  const [emailKeyword, setEmailKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  // 依據 email 關鍵字決定是否加查詢參數，符合流程 1.4
  const fetchUsers = async (keyword: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = keyword
        ? `/api/admin/users?email=${encodeURIComponent(keyword)}`
        : '/api/admin/users';
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch users');
      const data = await res.json();
      setUsers(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 初次載入取得全部使用者
  useEffect(() => {
    fetchUsers('');
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchUsers(emailKeyword);
  };

  const handleUserClick = (userId: string) => {
    setSelectedUserId(userId);
    // 跳轉至詳情頁（由路由決定實際行為）
    window.location.href = `/admin/users/${userId}`;
  };

  return (
    <div>
      <h1>使用者管理</h1>

      {/* email 搜尋框 */}
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="輸入 email 搜尋"
          value={emailKeyword}
          onChange={(e) => setEmailKeyword(e.target.value)}
        />
        <button type="submit">搜尋</button>
      </form>

      {loading && <p>載入中...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* 使用者列表：顯示姓名、email、狀態、建立時間 */}
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
              <tr
                key={user.id}
                onClick={() => handleUserClick(user.id)}
                style={{ cursor: 'pointer' }}
              >
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.status === 'active' ? '啟用' : '停用'}</td>
                <td>{new Date(user.createdAt).toLocaleDateString()}</td>
              </tr>
            ))}
            {users.length === 0 && (
              <tr>
                <td colSpan={4}>沒有符合的使用者</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default UserList;
