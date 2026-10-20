import path from 'node:path';
import fs from 'node:fs';

function loadTree(fileName) {
  const filePath = path.join(process.cwd(), 'data', fileName);
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

// Keeps only leaf nodes the user has permission for, and drops any
// group whose children all got filtered out.
function filterTree(nodes, user) {
  return nodes
    .map((node) => {
      if (node.children) {
        const children = filterTree(node.children, user);
        return children.length ? { ...node, children } : null;
      }
      return user.permissions.has(node.code) ? node : null;
    })
    .filter(Boolean);
}

export function getPortalSidebar(user) {
  return filterTree(loadTree('sidebar-portal.json'), user);
}

export function getAdminSidebar(user) {
  return filterTree(loadTree('sidebar-admin.json'), user);
}
