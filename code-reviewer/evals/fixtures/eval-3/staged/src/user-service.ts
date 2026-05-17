import { pool } from '../db';

// TODO: 之後要加分頁功能
export async function searchUsers(term: string) {
  const query = `SELECT id, name, email FROM users WHERE name LIKE '%${term}%' OR email LIKE '%${term}%'`;
  const result = await pool.query(query);
  return result.rows;
}

export async function getUserById(id: number) {
  const result = await pool.query(`SELECT * FROM users WHERE id = ${id}`);
  return result.rows[0] ?? null;
}

// 舊版實作，先保留
// export async function findUser(searchTerm: string) {
//   return pool.query('SELECT * FROM users WHERE name = $1', [searchTerm]);
// }
