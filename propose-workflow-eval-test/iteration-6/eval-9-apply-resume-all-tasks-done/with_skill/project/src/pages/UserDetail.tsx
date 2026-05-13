import React, { useState, useEffect } from 'react';

interface UserDetail {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'disabled';
  createdAt: string;
  orderCount: number;
}

interface Props {
  userId: string;
}

const UserDetail: React.FC<Props> = ({ userId }) => {
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusLoading, setStatusLoading] = useState(false);

  // 依使用者 id 取得詳情資料
  const fetchUserDetail = async () => {
    setLoading(true);
    const res = await fetch(`/api/admin/users/${userId}`);
    const data = await res.json();
    setUser(data);
    setLoading(false);
  };

  // 呼叫 PATCH API 更新帳號狀態，成功後同步更新畫面，失敗時顯示錯誤訊息
  const handleToggleStatus = async () => {
    if (!user) return;
    setStatusLoading(true);
    setError('');
    const nextStatus = user.status === 'active' ? 'disabled' : 'active';
    const res = await fetch(`/api/admin/users/${userId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: nextStatus }),
    });
    if (res.ok) {
      setUser({ ...user, status: nextStatus });
    } else {
      setError('操作失敗，請稍後再試');
    }
    setStatusLoading(false);
  };

  useEffect(() => {
    fetchUserDetail();
  }, [userId]);

  if (loading) return <p>載入中...</p>;
  if (!user) return <p>找不到使用者</p>;

  return (
    <div>
      <h2>使用者詳情</h2>
      <p>姓名：{user.name}</p>
      <p>Email：{user.email}</p>
      <p>建立時間：{user.createdAt}</p>
      <p>訂單數量：{user.orderCount}</p>
      <p>狀態：{user.status === 'active' ? '啟用' : '停用'}</p>
      <button onClick={handleToggleStatus} disabled={statusLoading}>
        {user.status === 'active' ? '停用' : '啟用'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default UserDetail;
