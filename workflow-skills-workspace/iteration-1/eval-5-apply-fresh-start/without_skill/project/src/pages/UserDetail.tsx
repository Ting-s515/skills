import React, { useState, useEffect } from 'react';

interface UserDetail {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'inactive';
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
  const [statusUpdating, setStatusUpdating] = useState(false);

  // 取得使用者詳情
  const fetchUserDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/admin/users/${userId}`);
      if (!response.ok) {
        throw new Error('取得使用者詳情失敗');
      }
      const data = await response.json();
      setUser(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '發生未知錯誤');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserDetail();
  }, [userId]);

  // 切換使用者帳號狀態（停用/啟用）
  const handleToggleStatus = async () => {
    if (!user) return;

    const newStatus = user.status === 'active' ? 'inactive' : 'active';
    setStatusUpdating(true);
    setError(null);

    try {
      const response = await fetch(`/api/admin/users/${userId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error('更新使用者狀態失敗');
      }

      // 成功後更新畫面狀態
      setUser((prev) => (prev ? { ...prev, status: newStatus } : prev));
    } catch (err) {
      // 失敗時顯示錯誤訊息，帳號狀態不變
      setError(err instanceof Error ? err.message : '發生未知錯誤');
    } finally {
      setStatusUpdating(false);
    }
  };

  if (loading) return <p>載入中...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!user) return null;

  return (
    <div>
      <h1>使用者詳情</h1>
      <p><strong>姓名：</strong>{user.name}</p>
      <p><strong>Email：</strong>{user.email}</p>
      <p><strong>建立時間：</strong>{user.createdAt}</p>
      <p><strong>訂單數量：</strong>{user.orderCount}</p>
      <p><strong>狀態：</strong>{user.status === 'active' ? '啟用' : '停用'}</p>
      <button
        onClick={handleToggleStatus}
        disabled={statusUpdating}
      >
        {user.status === 'active' ? '停用' : '啟用'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default UserDetail;
