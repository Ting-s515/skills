import React, { useState, useEffect } from 'react';

interface UserDetail {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'disabled';
  createdAt: string;
  orderCount: number;
}

interface UserDetailProps {
  userId: string;
}

const UserDetail: React.FC<UserDetailProps> = ({ userId }) => {
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [statusUpdating, setStatusUpdating] = useState(false);

  // 依照 userId 呼叫 GET /api/admin/users/:id 取得詳情
  const fetchUserDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/admin/users/${userId}`);
      if (!res.ok) throw new Error('載入使用者詳情失敗');
      const data: UserDetail = await res.json();
      setUser(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserDetail();
  }, [userId]);

  // 呼叫 PATCH /api/admin/users/:id/status 切換啟用/停用狀態
  // 成功後更新畫面狀態，失敗時顯示錯誤訊息且帳號狀態不變
  const handleToggleStatus = async () => {
    if (!user) return;
    const newStatus = user.status === 'active' ? 'disabled' : 'active';
    setStatusUpdating(true);
    setStatusError(null);
    try {
      const res = await fetch(`/api/admin/users/${userId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) throw new Error('更新狀態失敗，請稍後再試');
      // 成功後直接更新本地狀態，不重新呼叫 GET
      setUser({ ...user, status: newStatus });
    } catch (err) {
      setStatusError(err instanceof Error ? err.message : '未知錯誤');
    } finally {
      setStatusUpdating(false);
    }
  };

  if (loading) return <p>載入中...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!user) return null;

  const isActive = user.status === 'active';

  return (
    <div>
      <h1>使用者詳情</h1>
      <p>姓名：{user.name}</p>
      <p>Email：{user.email}</p>
      <p>建立時間：{user.createdAt}</p>
      <p>訂單數量：{user.orderCount}</p>
      <p>狀態：{isActive ? '啟用' : '停用'}</p>
      <button onClick={handleToggleStatus} disabled={statusUpdating}>
        {isActive ? '停用' : '啟用'}
      </button>
      {statusError && <p style={{ color: 'red' }}>{statusError}</p>}
    </div>
  );
};

export default UserDetail;
