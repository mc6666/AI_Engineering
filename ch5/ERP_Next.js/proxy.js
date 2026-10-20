import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import fs from 'node:fs';
import path from 'node:path';
import { db } from '@/lib/db';

const SESSION_SECRET = process.env.SESSION_SECRET || 'dev-only-insecure-secret-change-me';

// Path -> permission-code map, derived from the same sidebar JSON files that
// drive the menus, so a page's access rule can never drift from its menu entry.
let pathPermissionMap = null;
function getPathPermissionMap() {
  if (pathPermissionMap) return pathPermissionMap;
  const map = [];
  for (const file of ['sidebar-portal.json', 'sidebar-admin.json']) {
    const tree = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'data', file), 'utf8'));
    flatten(tree, map);
  }
  pathPermissionMap = map.sort((a, b) => b.path.length - a.path.length);
  return pathPermissionMap;
}
function flatten(nodes, out) {
  for (const node of nodes) {
    if (node.children) flatten(node.children, out);
    else out.push({ path: node.path, code: node.code });
  }
}

function hasPermission(userId, code) {
  return Boolean(
    db
      .prepare(
        `SELECT 1 FROM functions f
         JOIN role_functions rf ON rf.function_id = f.id
         JOIN user_roles ur ON ur.role_id = rf.role_id
         WHERE ur.user_id = ? AND f.code = ?`
      )
      .get(userId, code)
  );
}

export function proxy(request) {
  const { pathname } = request.nextUrl;

  const token = request.cookies.get('erp_session')?.value;
  let userId = null;
  if (token) {
    try {
      userId = jwt.verify(token, SESSION_SECRET).sub;
    } catch {
      userId = null;
    }
  }
  if (!userId) return NextResponse.redirect(new URL('/login', request.url));

  // Bare module landing pages (/portal, /admin) only require being logged in.
  if (pathname === '/portal' || pathname === '/admin') return NextResponse.next();

  const match = getPathPermissionMap().find(
    (m) => pathname === m.path || pathname.startsWith(m.path + '/')
  );
  if (!match) return NextResponse.next();

  if (!hasPermission(userId, match.code)) {
    const url = new URL('/portal', request.url);
    url.searchParams.set('error', `Forbidden: missing permission ${match.code}`);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/portal/:path*', '/admin/:path*'],
};
