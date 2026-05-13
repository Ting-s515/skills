import React, { useState, useEffect } from 'react';

// 使用者詳情資料結構
interface UserDetail {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'inactive';
  createdAt: string;
  orderCount: number;
}

// 呼叫 GET /api/admin/users/:id 取得使用者詳情
async function fetchUserDetail(userId: string): Promise<UserDetail> {
  const response = await fetch(`/api/admin/users/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user detail');
  }
  return response.json();
}

// 呼叫 PATCH /api/admin/users/:id/status 更新使用者狀態
async function updateUserStatus(
  userId: string,
  status: 'active' | 'inactive'
): Promise<void> {
  const response = await fetch(`/api/admin/users/${userId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!response.ok) {
    throw new Error('Failed to update user status');
  }
}

interface UserDetailProps {
  userId: string;
}

const UserDetailPage: React.FC<UserDetailProps> = ({ userId }) => {
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  // 載入使用者詳情
  const loadUserDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchUserDetail(userId);
      setUser(result);
    } catch (err) {
      setError('無法載入使用者詳情，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUserDetail();
  }, [userId]);

  // 切換使用者啟用/停用狀態
  const handleToggleStatus = async () => {
    if (!user) return;

    const newStatus = user.status === 'active' ? 'inactive' : 'active';
    setUpdatingStatus(true);
    setStatusError(null);

    try {
      await updateUserStatus(userId, newStatus);
      // 成功後更新本地狀態，避免重新呼叫 API
      setUser({ ...user, status: newStatus });
    } catch (err) {
      // 失敗時顯示錯誤訊息，狀態保持不變
      setStatusError('操作失敗，請稍後再試');
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) return <p>載入中...</p>;
  if (error) return <p>{error}</p>;
  if (!user) return null;

  return (
    <div>
      <h1>使用者詳情</h1>
      <p>姓名：{user.name}</p>
      <p>Email：{user.email}</p>
      <p>建立時間：{user.createdAt}</p>
      <p>訂單數量：{user.orderCount}</p>
      <p>狀態：{user.status === 'active' ? '啟用' : '停用'}</p>
      {statusError && <p>{statusError}</p>}
      <button onClick={handleToggleStatus} disabled={updatingStatus}>
        {user.status === 'active' ? '停用' : '啟用'}
      </button>
    </div>
  );
};

export default UserDetailPage;
export { fetchUserDetail, updateUserStatus };
export type { UserDetail };
