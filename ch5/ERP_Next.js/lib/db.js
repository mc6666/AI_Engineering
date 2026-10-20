import Database from 'better-sqlite3';
import bcrypt from 'bcryptjs';
import path from 'node:path';
import fs from 'node:fs';

const DB_PATH = path.join(process.cwd(), 'data', 'erp.db');
const SCHEMA_PATH = path.join(process.cwd(), 'lib', 'schema.sql');

// Sidebar JSON files double as the source of truth for permission "functions":
// every leaf node's `code` becomes a row in the functions table.
function flattenFunctionCodes(nodes, module) {
  const out = [];
  for (const node of nodes) {
    if (node.children) {
      out.push(...flattenFunctionCodes(node.children, module));
    } else {
      out.push({ code: node.code, name: node.label, module });
    }
  }
  return out;
}

function seedIfEmpty(conn) {
  const { n } = conn.prepare('SELECT COUNT(*) AS n FROM functions').get();
  if (n > 0) return;

  const portal = JSON.parse(
    fs.readFileSync(path.join(process.cwd(), 'data', 'sidebar-portal.json'), 'utf8')
  );
  const admin = JSON.parse(
    fs.readFileSync(path.join(process.cwd(), 'data', 'sidebar-admin.json'), 'utf8')
  );
  const allFunctions = [
    ...flattenFunctionCodes(portal, 'portal'),
    ...flattenFunctionCodes(admin, 'admin'),
  ];

  const insertFn = conn.prepare(
    'INSERT INTO functions (code, name, module) VALUES (?, ?, ?)'
  );
  const insertRoleFn = conn.prepare(
    'INSERT INTO role_functions (role_id, function_id) VALUES (?, ?)'
  );

  const seedTxn = conn.transaction(() => {
    const roleId = conn
      .prepare('INSERT INTO roles (name, description) VALUES (?, ?)')
      .run('Administrator', '系統管理員，擁有所有功能權限').lastInsertRowid;

    for (const fn of allFunctions) {
      const fnId = insertFn.run(fn.code, fn.name, fn.module).lastInsertRowid;
      insertRoleFn.run(roleId, fnId);
    }

    const passwordHash = bcrypt.hashSync('admin123', 10);
    const userId = conn
      .prepare(
        'INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)'
      )
      .run('admin', 'admin@example.com', passwordHash, 'System Administrator').lastInsertRowid;
    conn.prepare('INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)').run(userId, roleId);
  });
  seedTxn();
}

function createConnection() {
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
  const conn = new Database(DB_PATH);
  conn.pragma('journal_mode = WAL');
  conn.pragma('foreign_keys = ON');
  conn.exec(fs.readFileSync(SCHEMA_PATH, 'utf8'));
  seedIfEmpty(conn);
  return conn;
}

// Reuse a single connection across hot-reloads in dev.
const globalForDb = globalThis;
export const db = globalForDb.__erpDb || (globalForDb.__erpDb = createConnection());

// Document numbers only need to be unique, not sequential, so a timestamp +
// random suffix avoids a dedicated per-document-type sequence table.
export function nextDocNo(prefix) {
  const stamp = new Date();
  const y = stamp.getFullYear();
  const m = String(stamp.getMonth() + 1).padStart(2, '0');
  const d = String(stamp.getDate()).padStart(2, '0');
  const rand = Math.floor(Math.random() * 900 + 100);
  return `${prefix}${y}${m}${d}${String(Date.now()).slice(-5)}${rand}`;
}
