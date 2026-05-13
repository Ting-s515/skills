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

// 取得使用者詳情
async function fetchUserDetail(userId: string): Promise<UserDetail> {
  const response = await fetch(`/api/admin/users/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user detail');
  }
  return response.json();
}

// 呼叫 PATCH API 更新使用者帳號狀態
async function updateUserStatus(
  userId: string,
  newStatus: 'active' | 'disabled'
): Promise<void> {
  const response = await fetch(`/api/admin/users/${userId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus }),
  });
  if (!response.ok) {
    throw new Error('Failed to update user status');
  }
}

const UserDetail: React.FC<Props> = ({ userId }) => {
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);

  useEffect(() => {
    loadUser();
  }, [userId]);

  const loadUser = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchUserDetail(userId);
      setUser(data);
    } catch {
      setError('載入使用者詳情失敗');
    } finally {
      setLoading(false);
    }
  };

  // 根據目前狀態切換停用/啟用
  const handleToggleStatus = async () => {
    if (!user) return;
    const newStatus = user.status === 'active' ? 'disabled' : 'active';
    setStatusLoading(true);
    setError(null);
    try {
      await updateUserStatus(userId, newStatus);
      // 成功後更新本地狀態，反映最新結果
      setUser({ ...user, status: newStatus });
    } catch {
      setError('更新帳號狀態失敗');
    } finally {
      setStatusLoading(false);
    }
  };

  if (loading) return <p>載入中...</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!user) return null;

  return (
    <div>
      <h1>使用者詳情</h1>
      <dl>
        <dt>姓名</dt>
        <dd data-testid="user-name">{user.name}</dd>
        <dt>Email</dt>
        <dd data-testid="user-email">{user.email}</dd>
        <dt>建立時間</dt>
        <dd data-testid="user-created-at">{user.createdAt}</dd>
        <dt>訂單數量</dt>
        <dd data-testid="user-order-count">{user.orderCount}</dd>
        <dt>狀態</dt>
        <dd data-testid="user-status">
          {user.status === 'active' ? '啟用' : '停用'}
        </dd>
      </dl>
      <button
        onClick={handleToggleStatus}
        disabled={statusLoading}
        data-testid="toggle-status-btn"
      >
        {user.status === 'active' ? '停用' : '啟用'}
      </button>
      {error && <p role="alert" data-testid="status-error">{error}</p>}
    </div>
  );
};

export default UserDetail;
