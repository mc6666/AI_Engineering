import Link from 'next/link';
import { listRoles } from '@/lib/rbac';
import { deleteRoleAction } from '@/app/actions/rbac';

export default async function RolesPage() {
  const roles = listRoles();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>角色管理</h2>
        <Link href="/admin/roles/new" className="btn btn-primary">
          新增角色
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>角色名稱</th>
            <th>說明</th>
            <th>功能數量</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {roles.map((r) => (
            <tr key={r.id}>
              <td>
                <Link href={`/admin/roles/${r.id}`}>{r.name}</Link>
              </td>
              <td>{r.description || '-'}</td>
              <td>{r.function_count}</td>
              <td>
                <form action={deleteRoleAction}>
                  <input type="hidden" name="id" value={r.id} />
                  <button type="submit" className="btn btn-sm btn-danger">
                    刪除
                  </button>
                </form>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
