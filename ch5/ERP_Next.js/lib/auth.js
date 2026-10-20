import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { db } from './db';

const SESSION_COOKIE = 'erp_session';
const SESSION_SECRET = process.env.SESSION_SECRET || 'dev-only-insecure-secret-change-me';
const SESSION_TTL_SECONDS = 60 * 60 * 8; // 8 hours

export function registerUser({ username, email, password, fullName }) {
  if (!username || !email || !password || !fullName) {
    throw new Error('username, email, password and fullName are required');
  }
  const existing = db
    .prepare('SELECT id FROM users WHERE username = ? OR email = ?')
    .get(username, email);
  if (existing) throw new Error('Username or email already registered');

  const passwordHash = bcrypt.hashSync(password, 10);
  const result = db
    .prepare(
      `INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)`
    )
    .run(username, email, passwordHash, fullName);
  return result.lastInsertRowid;
}

export function verifyLogin({ username, password }) {
  const user = db
    .prepare('SELECT * FROM users WHERE username = ? AND is_active = 1')
    .get(username);
  if (!user) throw new Error('Invalid username or password');
  if (!bcrypt.compareSync(password, user.password_hash)) {
    throw new Error('Invalid username or password');
  }
  return user;
}

export function changePassword({ userId, currentPassword, newPassword }) {
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
  if (!user) throw new Error('User not found');
  if (!bcrypt.compareSync(currentPassword, user.password_hash)) {
    throw new Error('Current password is incorrect');
  }
  const newHash = bcrypt.hashSync(newPassword, 10);
  db.prepare('UPDATE users SET password_hash = ? WHERE id = ?').run(newHash, userId);
}

export async function createSession(user) {
  const token = jwt.sign({ sub: user.id, username: user.username }, SESSION_SECRET, {
    expiresIn: SESSION_TTL_SECONDS,
  });
  const store = await cookies();
  store.set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    maxAge: SESSION_TTL_SECONDS,
    path: '/',
  });
}

export async function destroySession() {
  const store = await cookies();
  store.delete(SESSION_COOKIE);
}

// Returns the logged-in user (with roles/functions resolved) or null.
export async function getCurrentUser() {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  if (!token) return null;

  let payload;
  try {
    payload = jwt.verify(token, SESSION_SECRET);
  } catch {
    return null;
  }

  const user = db
    .prepare('SELECT id, username, email, full_name, is_active FROM users WHERE id = ?')
    .get(payload.sub);
  if (!user || !user.is_active) return null;

  const functionCodes = db
    .prepare(
      `SELECT DISTINCT f.code
       FROM functions f
       JOIN role_functions rf ON rf.function_id = f.id
       JOIN user_roles ur ON ur.role_id = rf.role_id
       WHERE ur.user_id = ?`
    )
    .all(user.id)
    .map((r) => r.code);

  const roles = db
    .prepare(
      `SELECT r.id, r.name FROM roles r JOIN user_roles ur ON ur.role_id = r.id WHERE ur.user_id = ?`
    )
    .all(user.id);

  return { ...user, roles, permissions: new Set(functionCodes) };
}

export async function requireUser() {
  const user = await getCurrentUser();
  if (!user) redirect('/login');
  return user;
}

export function hasPermission(user, functionCode) {
  return Boolean(user?.permissions?.has(functionCode));
}

export function hasAnyPermissionPrefix(user, prefix) {
  if (!user?.permissions) return false;
  for (const code of user.permissions) {
    if (code.startsWith(prefix)) return true;
  }
  return false;
}

export async function requirePermission(functionCode) {
  const user = await requireUser();
  if (!hasPermission(user, functionCode)) {
    redirect(`/portal?error=${encodeURIComponent('Forbidden: missing permission ' + functionCode)}`);
  }
  return user;
}
