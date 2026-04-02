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
  const [error, setError] = useState<string | null>(null);

  // 依照 email 關鍵字決定 API query，無輸入時取全部使用者
  const fetchUsers = async (keyword: string) => {
    setLoading(true);
    setError(null);
    try {
      const query = keyword ? `?email=${encodeURIComponent(keyword)}` : '';
      const res = await fetch(`/api/admin/users${query}`);
      if (!res.ok) throw new Error('載入使用者列表失敗');
      const data: User[] = await res.json();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  // 初始載入全部使用者
  useEffect(() => {
    fetchUsers('');
  }, []);

  // 搜尋框變更時重新呼叫 API 篩選
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
        placeholder="依 email 搜尋"
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
