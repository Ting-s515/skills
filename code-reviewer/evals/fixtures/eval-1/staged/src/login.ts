import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { User } from '../models/User';

export async function loginHandler(req: Request, res: Response) {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(422).json({ error: '缺少必填欄位' });
  }

  const user = await User.findOne({ where: { email } });
  if (!user) {
    // 規格要求 401，且不可揭露使用者是否存在（避免帳號枚舉攻擊）
    return res.status(404).json({ error: '使用者不存在' });
  }

  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    // 規格要求 401
    return res.status(400).json({ error: '密碼錯誤' });
  }

  const token = jwt.sign(
    { userId: user.id },
    process.env.JWT_SECRET as string,
    { expiresIn: '7d' }
  );

  return res.status(200).json({
    token,
    user: { id: user.id, email: user.email },
  });
}
