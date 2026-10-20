import bcrypt from 'bcryptjs';
import { db } from './db';

// ---------- Users ----------
export function listUsers() {
  return db
    .prepare(
      `SELECT u.id, u.username, u.email, u.full_name, u.is_active, u.created_at,
              GROUP_CONCAT(r.name, ', ') AS role_names
       FROM users u
       LEFT JOIN user_roles ur ON ur.user_id = u.id
       LEFT JOIN roles r ON r.id = ur.role_id
       GROUP BY u.id
       ORDER BY u.username`
    )
    .all();
}

export function getUser(id) {
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(id);
  if (!user) return null;
  const roleIds = db
    .prepare('SELECT role_id FROM user_roles WHERE user_id = ?')
    .all(id)
    .map((r) => r.role_id);
  return { ...user, roleIds };
}

export function createUserByAdmin({ username, email, fullName, password, roleIds = [] }) {
  const existing = db
    .prepare('SELECT id FROM users WHERE username = ? OR email = ?')
    .get(username, email);
  if (existing) throw new Error('Username or email already in use');

  const passwordHash = bcrypt.hashSync(password, 10);
  const txn = db.transaction(() => {
    const userId = db
      .prepare(
        'INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)'
      )
      .run(username, email, passwordHash, fullName).lastInsertRowid;
    const insertUR = db.prepare('INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)');
    for (const roleId of roleIds) insertUR.run(userId, roleId);
    return userId;
  });
  return txn();
}

export function updateUserByAdmin(id, { fullName, email, isActive, roleIds = [] }) {
  const txn = db.transaction(() => {
    db.prepare(
      'UPDATE users SET full_name = ?, email = ?, is_active = ? WHERE id = ?'
    ).run(fullName, email, isActive ? 1 : 0, id);
    db.prepare('DELETE FROM user_roles WHERE user_id = ?').run(id);
    const insertUR = db.prepare('INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)');
    for (const roleId of roleIds) insertUR.run(id, roleId);
  });
  txn();
}

export function deleteUser(id) {
  db.prepare('DELETE FROM users WHERE id = ?').run(id);
}

// ---------- Roles ----------
export function listRoles() {
  return db
    .prepare(
      `SELECT r.id, r.name, r.description, COUNT(rf.function_id) AS function_count
       FROM roles r
       LEFT JOIN role_functions rf ON rf.role_id = r.id
       GROUP BY r.id
       ORDER BY r.name`
    )
    .all();
}

export function getRole(id) {
  const role = db.prepare('SELECT * FROM roles WHERE id = ?').get(id);
  if (!role) return null;
  const functionIds = db
    .prepare('SELECT function_id FROM role_functions WHERE role_id = ?')
    .all(id)
    .map((r) => r.function_id);
  return { ...role, functionIds };
}

export function createRole({ name, description, functionIds = [] }) {
  const txn = db.transaction(() => {
    const roleId = db
      .prepare('INSERT INTO roles (name, description) VALUES (?, ?)')
      .run(name, description || null).lastInsertRowid;
    const insertRF = db.prepare(
      'INSERT INTO role_functions (role_id, function_id) VALUES (?, ?)'
    );
    for (const fnId of functionIds) insertRF.run(roleId, fnId);
    return roleId;
  });
  return txn();
}

export function updateRole(id, { name, description, functionIds = [] }) {
  const txn = db.transaction(() => {
    db.prepare('UPDATE roles SET name = ?, description = ? WHERE id = ?').run(
      name,
      description || null,
      id
    );
    db.prepare('DELETE FROM role_functions WHERE role_id = ?').run(id);
    const insertRF = db.prepare(
      'INSERT INTO role_functions (role_id, function_id) VALUES (?, ?)'
    );
    for (const fnId of functionIds) insertRF.run(id, fnId);
  });
  txn();
}

export function deleteRole(id) {
  db.prepare('DELETE FROM roles WHERE id = ?').run(id);
}

// ---------- Functions (read-only; sourced from the sidebar JSON trees) ----------
export function listFunctions() {
  return db.prepare('SELECT * FROM functions ORDER BY module, code').all();
}
