import React, { useEffect, useState } from 'react';

interface UserDetail {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  orderCount: number;
  status: 'active' | 'disabled';
}

// 呼叫後端 API 取得單一使用者詳情
async function fetchUserDetail(id: string): Promise<UserDetail> {
  const res = await fetch(`/api/admin/users/${id}`);
  if (!res.ok) throw new Error('Failed to fetch user detail');
  return res.json();
}

// 呼叫後端 API 更新使用者狀態（停用或啟用）
async function updateUserStatus(
  id: string,
  status: 'active' | 'disabled'
): Promise<void> {
  const res = await fetch(`/api/admin/users/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to update user status');
}

interface UserDetailProps {
  userId: string;
}

const UserDetailPage: React.FC<UserDetailProps> = ({ userId }) => {
  const [user, setUser] = useState<UserDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    setError(null);
    fetchUserDetail(userId)
      .then(setUser)
      .catch(() => setError('載入使用者詳情失敗'));
  }, [userId]);

  // 切換停用/啟用狀態：成功後更新本地狀態，失敗時顯示錯誤訊息且不改變現有狀態
  const handleToggleStatus = async () => {
    if (!user) return;

    const newStatus = user.status === 'active' ? 'disabled' : 'active';
    setStatusError(null);
    setIsUpdating(true);

    try {
      await updateUserStatus(userId, newStatus);
      // 成功後更新畫面狀態
      setUser({ ...user, status: newStatus });
    } catch {
      // 失敗時顯示錯誤訊息，帳號狀態不變
      setStatusError('更新狀態失敗，請稍後再試');
    } finally {
      setIsUpdating(false);
    }
  };

  if (error) return <p role="alert">{error}</p>;
  if (!user) return <p>載入中...</p>;

  return (
    <div>
      <h1>使用者詳情</h1>
      <dl>
        <dt>姓名</dt>
        <dd>{user.name}</dd>
        <dt>Email</dt>
        <dd>{user.email}</dd>
        <dt>建立時間</dt>
        <dd>{user.createdAt}</dd>
        <dt>訂單數量</dt>
        <dd>{user.orderCount}</dd>
        <dt>狀態</dt>
        <dd>{user.status === 'active' ? '啟用' : '停用'}</dd>
      </dl>
      <button onClick={handleToggleStatus} disabled={isUpdating}>
        {user.status === 'active' ? '停用' : '啟用'}
      </button>
      {statusError && <p role="alert">{statusError}</p>}
    </div>
  );
};

export default UserDetailPage;
